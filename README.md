python-alacard
==============

Python library to check Euroticket à la card balance and history.

Requirements
-----

- Python 3.x


Usage
-----

```bash
$ ./alacard.py -h
usage: alacard.py [-h] -u username -p password [-m]

Check Euroticket à la card balance and history.

optional arguments:
  -h, --help   show this help message and exit
  -u username  the card number
  -p password  the card password
  -m           display card movements
```

Example
-------

```bash
$ ./alacard.py -u 1234567890123456 -p 235711 -m

Holder Name:         John Doe
Card Number:         1234567890123456
Expiration Date:     06/2016
Outstanding Balance: 126.29
Current Balance:     105.84

 | Id       | Date      | Type      | Description                          | Debit | Debit  | Balance | 
 | 11111111 | 8/Out/13  | Movimento | NAMUR               1990-083 LISBOA  | 11.5  | 0.0    | 105.84  | 
 | 22222222 | 7/Out/13  | Movimento | EL CORTE INGLES LISBLISBOA           | 7.95  | 0.0    | 117.34  | 
 | 33333333 | 12/Set/13 | Movimento | REST CHINES         LISBOA           | 7.15  | 0.0    | 125.29  | 
 | 44444444 | 10/Set/13 | Movimento | CONTINENTE          2724-520 AMADORA | 18.94 | 0.0    | 132.44  | 
 | 55555555 | 8/Set/13  | Movimento | R C SANCHES   VASCO LISBOA           | 7.4   | 0.0    | 151.38  | 
```

Avoiding Repetition
-------------------

When you get tired of typing in you card number and password, you may create an alias.

```bash
$ alias showmethemoney='python alacard.py -u 1234567890123456 -p 235711'
$ showmethemoney
$ showmethemoney -m
```
