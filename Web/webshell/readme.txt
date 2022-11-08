you can read flag:
https://www.geeksforgeeks.org/files-class-readstring-method-in-java-with-examples/
then leak information by side channel info
> exec(cond?params.cmd:"const")
if cond is true, the checker will report a HIGH risk level (because you can control the arg of exec)
if cond is false, the checker will report a MEDIUM risk level (arg of exec cant be controlled)
