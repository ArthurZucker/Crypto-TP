# CRYPTAvancée
Here, in order to work on the TP, use `telnet crypta.fil.cool`
Use `-x` for encryption of the datastream

## Regristration :
I used `openssl ecparam -name wap-wsg-idm-ecid-wtls7 -genkey -out private-key.pem` then `openssl ec -in private-key.pem -pubout -out public-key.pem`
Now I have to sign a text :
`openssl dgst -sha256 -sign private-key.pem  -out /tmp/sign.sha256 challenge.txt`

## Exercices in TME room

- [x] #5 TME #1 : équation linéaire diophantienne
- [x] #7 TME #2 : théorème des restes chinois
- [x] #11 TME #3 : ordre d'un groupe
- [x] #13 TME #4 : pohlig
- [x] Attaque admin

## Downloader and uploader :

- Use downloader on "me", then should we modify line 382?