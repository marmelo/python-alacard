python-alacard
==============

Python library to check Euroticket à la card balance and recent history.

https://www.euroticket-alacard.pt/

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

| Id    | Date      | Type      | Description             | Debit  | Credit | Balance |
| 11111 | 8/Out/13  | Movimento | NAMUR           LISBOA  | €11.50 | €0.00  | 105.84  |
| 22222 | 7/Out/13  | Movimento | EL CORTE INGLES LISBOA  | €7.95  | €0.00  | 117.34  |
| 33333 | 12/Set/13 | Movimento | REST CHINES     LISBOA  | €7.15  | €0.00  | 125.29  |
| 44444 | 10/Set/13 | Movimento | CONTINENTE      AMADORA | €18.94 | €0.00  | 132.44  |
| 55555 | 8/Set/13  | Movimento | R C SANCHES     LISBOA  | €7.40  | €0.00  | 151.38  |
```

Avoiding Repetition
-------------------

When you get tired of typing in you card number and password, you may create an alias.

```bash
$ alias showmethemoney='./alacard.py -u 3141592653589793 -p 577215'
$ showmethemoney
$ showmethemoney -m
```
