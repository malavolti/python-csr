# python-csr
## Purpose
Generate a key and certificate request.

## Information
You'll notice there is a csrgen and csrgen35. This corresponds to their respective Python versions.
- csrgen uses Python 2.7
- csrgen35 uses Python 3.5

## Installation / Dependencies
The following modules are required:
- OpenSSL (pyopenssl)
- Argparse (argparse)

I've included a setup.py that will install these dependencies if you run:
```
python setup.py install
```

## Usage
csrgen [fqdn]

```
python csrgen -n test.test.com
```

When more than one hostname is provided, a SAN (Subject Alternate Name)
certificate and request are generated.  This can be acheived by adding a -s.

csrgen <hostname> -s <san0> <san1>

```
python csrgen -n test.test.com -s mushu.test.com pushu.test.com
```

# TODO
- Consolidate Python 2.7 & 3.5
- For CLI (not -f), ensure a -n is provided or "fail" gracefully.
- Have the C, ST, L, O, OU stored in a .conf file and ask if
   these are the settings the user wants to use before running.
- Turn this into a Class.
