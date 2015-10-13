## senv

senv = "secure env", it loads enviornment variables from your keychain (for now it supports Mac only)

Adding enviornment variables to keychain using account `test_a` .
```
senv add test_a a=AAA b=BBB
```

Show enviornment variables binding to that account
```bash
# 
senv show test_a
[account]: test_a
====================
a=********
b=********
```

Show enviorment variables without mask.

```bash
$> senv show test_a  --unmask
[account]: test_a
====================
a=AAA
b=BBB
```

With this you can add your aws key to keychain.

```
$> senv show ndm_aws
[account]: ndm_aws
====================
AWS_ACCESS_KEY_ID=AS****************IA
AWS_SECRET_ACCESS_KEY=A2************************************NL
AWS_SECURITY_TOKEN=AQ********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************AF
```

So I can simly do 
```
$> senv run ndm_aws aws s3 ls s3://my-bucket/
                           PRE my_folder/
                           PRE my_folder2/
                           ....
```

If you have multiple awskey like me, you'd better leverage `alias`.

```
# Leave this in your .bash_profile
alias k1='senv run aws_k1'
alias k2='senv run aws_k2'
alias k3='senv run aws_k3'
```

And you can simply do:
```
k1 aws s3 ls s3://k1-bucket/...
k2 aws s3 ls s3://k2-bucket/...
k3 aws s3 ls s3://k2-bucket/...
```



