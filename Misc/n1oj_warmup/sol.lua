local function solve()
	local function str2bint(s)
        local r={}
        for i=#s,1,-1 do
            table.insert(r,s:byte(i)-48)
        end
        for i=1,5000 do
            table.insert(r,0)
        end
        return r
    end
    local function bint2str(A)
        local res=""
        local fg = false
        for i=#A,1,-1 do
            if A[i]~=0 or fg then
                res=res..string.char(A[i]+48)
                fg=true
            end
        end
        return res
    end
    local function add_bint(A,B)
        local res={}
        local c=0
        for i=1,5000 do
            local t=A[i]+B[i]+c
            c=t//10
            table.insert(res,t%10)
        end
        return res
    end
    local function getline()
        local res=gets()
        if res:sub(-1,-1)=="\n" then
            res=res:sub(0,-2)
        end
        return res
    end
    print(bint2str(add_bint(str2bint(getline()),str2bint(getline()))))
end
solve()
