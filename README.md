## senv

senv = "secure env", it loads enviornment variables from your keychain (for now it supports Mac only)

Adding enviornment variables to keychain using account `test_a` .
```bash
$> senv add test_a a=AAA b=BBB
```

Show enviornment variables binding to that account
```bash
$> senv show test_a
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

```bash
$> senv show my_aws
[account]: my_aws
====================
AWS_ACCESS_KEY_ID=AS****************IA
AWS_SECRET_ACCESS_KEY=A2************************************NL
AWS_SECURITY_TOKEN=AQ********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************AF
```

So I can simly do 
```bash
$> senv run my_aws aws s3 ls s3://my-bucket/
                           PRE my_folder/
                           PRE my_folder2/
                           ....
```

If you have multiple awskey like me, you'd better leverage `alias`.

```bash
# Leave this in your .bash_profile
alias k1='senv run aws_k1'
alias k2='senv run aws_k2'
alias k3='senv run aws_k3'
```

And you can simply do:
```bash
$> k1 aws s3 ls s3://k1-bucket/...
$> k2 aws s3 ls s3://k2-bucket/...
$> k3 aws s3 ls s3://k3-bucket/...
```

### Installations

I haven't implemented a pip package, yet. As [senv](#senv) use the standard lib ships with python 2.x, so doesn't really need to pip install it.

You can just download the [senv.py](https://raw.githubusercontent.com/tly1980/senv/master/src/senv.py) to your path.

```bash
wget https://raw.githubusercontent.com/tly1980/senv/master/src/senv.py -O /usr/local/bin/senv

chmod a+x /usr/local/bin/senv
```

### Usages

It supports following actions:

1. add
2. show
3. run
4. del

```bash
$> senv add --help
usage: add [-h] [--service SERVICE] [--dry] [-i]
           account [variables [variables ...]]

add or update environment variables to keychain.

positional arguments:
  account
  variables

optional arguments:
  -h, --help         show this help message and exit
  --service SERVICE
  --dry
  -i, --interative
```

```bash
$> senv show --help
usage: show [-h] [--unmask] account

show environment variables from keychain.

positional arguments:
  account

optional arguments:
  -h, --help  show this help message and exit
  --unmask
```


```bash
$> senv run --help
usage: run [-h] account cmd [cmd ...]

load environment variables from keychain and execute your command.

positional arguments:
  account
  cmd

optional arguments:
  -h, --help  show this help message and exit
```

```bash
$> senv del --help
usage: del [-h] [--dry] account variables [variables ...]

del environment variables from keychain.

positional arguments:
  account
  variables

optional arguments:
  -h, --help  show this help message and exit
  --dry
```