# i18n
we use gettext to implement language system on AART

# AART i18n structure
file structure is as follows
```
locales
|-- tw
|   |-- LC_MESSAGES
|       |-- base.mo
|       |-- base.po
|-- base.pot
```

1. change all the output to the format _("hello world")
2. generate base.pot by `pygettext -d base -o locales/base.pot src/main.py src/welcome/welcome.py...`
3. copy base.pot to LC_MESSAGES `cp locales/base.pot locales/tw/LC_MESSAGES/base.po`
4. generate base.mo file by `msgfmt -o locales/tw/LC_MESSAGES/base.mo locales/tw/LC_MESSAGES/base.po`

# Usage
```
tw = gettext.translation(
    "base",
    localedir="./locales",
    languages=["tw"]
)
tw.install()
_ = tw.gettext
```
+ note: same msgid will only effect one of it

# Reference
https://medium.com/i18n-and-l10n-resources-for-developers/how-to-translate-python-applications-with-the-gnu-gettext-module-5c1c085041bd
