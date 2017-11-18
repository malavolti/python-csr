#!/usr/bin/env python3
#
# Generate a key, self-signed certificate, and certificate request.
# Usage: csrgen <fqdn>
#
# When more than one hostname is provided, a SAN (Subject Alternate Name)
# certificate and request are generated.  This can be acheived by adding -s.
# Usage: csrgen <hostname> -s <san0> <san1>
#
# Author: Courtney Cotton <cotton@cottoncourtney.com> 06-25-2014

# mod'd for python 3.5


# Libraries/Modules
from OpenSSL import crypto, SSL
import argparse
import yaml


def getCSRSubjects():
    while True:
        C  = raw_input("Enter your Country Name (2 letter code) [US]: ")
        if len(C) != 2:
          print "You must enter two letters. You entered %r" % (C)
          continue
        ST = raw_input("Enter your State or Province <full name> []:California: ")
        if len(ST) == 0:
          print "Please enter your State or Province."
          continue
        L  = raw_input("Enter your (Locality Name (eg, city) []:San Francisco: ")
        if len(L) == 0:
          print "Please enter your City."
          continue
        O  = raw_input("Enter your Organization Name (eg, company) []:FTW Enterprise: ")
        if len(L) == 0:
           print "Please enter your Organization Name."
           continue
        OU = raw_input("Enter your Organizational Unit (eg, section) []:IT: ")
        if len(OU) == 0:
          print "Please enter your OU."
          continue
        break
    return C, ST, L, O, OU

    # Allows you to permanently set values required for CSR
    # To use, comment raw_input and uncomment this section.
    # C  = 'US'
    # ST = 'New York'
    # L  = 'Location'
    # O  = 'Organization'
    # OU = 'Organizational Unit'

# Generate Certificate Signing Request (CSR)
def generateCSR(nodename, req_info, dest, sans=[]):
   csrfile = 'host.csr'
   keyfile = 'host.key'
   TYPE_RSA = crypto.TYPE_RSA
   # Appends SAN to have 'DNS:'
   ss = []
   for i in sans:
      ss.append("DNS: %s" % i)
   ss = ", ".join(ss)

   req = crypto.X509Req()
   req.get_subject().CN = nodename

   if(req_info == 'y' or req_info == 'Y' or req_info == 'yes' or req_info == 'Yes'):
      C, ST, L, O, OU = getCSRSubjects()
      req.get_subject().countryName = C
      req.get_subject().stateOrProvinceName = ST
      req.get_subject().localityName = L
      req.get_subject().organizationName = O
      req.get_subject().organizationalUnitName = OU

   # Add in extensions
   # added bytearray to string
   # before -> "keyUsage"
   # after  -> b"keyUsage"

   base_constraints = ([
      crypto.X509Extension(b"keyUsage", False, b"Digital Signature, Non Repudiation, Key Encipherment"),
      crypto.X509Extension(b"basicConstraints", False, b"CA:FALSE"),
   ])
   x509_extensions = base_constraints
   # If there are SAN entries, append the base_constraints to include them.
   if ss:
      san_constraint = crypto.X509Extension(b"subjectAltName", False, ss)
      x509_extensions.append(san_constraint)
   req.add_extensions(x509_extensions)
   # Utilizes generateKey function to kick off key generation.
   key = generateKey(TYPE_RSA, 2048)
   req.set_pubkey(key)

   # change to sha 256?
   # req.sign(key, "sha1")
   req.sign(key, "sha256")

   generateFiles(csrfile, req)
   generateFiles(keyfile, key)

   return req


# Generate Private Key
def generateKey(type, bits):
    key = crypto.PKey()
    key.generate_key(type, bits)
    return key


# Generate .csr/key files.
def generateFiles(mkFile, request):
   if mkFile == 'host.csr':
      f = open(mkFile, "wb")
      f.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, request))
      f.close()

      # print test
      #print(crypto.dump_certificate_request(crypto.FILETYPE_PEM, request))

   elif mkFile == 'host.key':
      f = open(mkFile, "wb")
      f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, request))
      f.close()
   else:
      print("Failed.")
      exit()

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument("-n", "--name", help="Provide the FQDN", action="store", default="")
   parser.add_argument("-d", "--dest", help="Provide the destination PATH", action="store", default="")
   parser.add_argument("-r", "--req_info", help="Set C,ST,L,O,OU? [y|n]", action="store", default="n")
   parser.add_argument("-s", "--san", help="SANS", action="store", nargs='*', default="")
   args = parser.parse_args()

   # Variables from CLI Parser (Argparse)
   hostname = args.name
   dest = args.dest
   sans = args.san

   # Run the primary function(s) based on input.
   if (hostname and dest):
      generateCSR(hostname,req_info,dest,sans)
   else:
      print("!!! FQDN(--name) or DESTINATION(--dest) missing !!!\n")
      parser.print_help()
