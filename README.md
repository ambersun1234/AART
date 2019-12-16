# Athlete analysis of real time sports events( AART )
[![Build Status](https://travis-ci.com/ambersun1234/AART.svg?token=e57vJgMEsZsXRodR9BkR&branch=master)](https://travis-ci.com/ambersun1234/AART)
[![License](https://img.shields.io/badge/License-aart-lightgray)](./LICENSE)

**AART** represents the athlete posture identification and tracking on video and webcam.

### Features
+ Real time athlete analysis
+ User-friendly GUI interface
+ Auto-save sports competition highlight
+ Providing language system( Traditional Chinese , English )

### Clone repo
```=1
git clone https://github.com/ambersun1234/AART.git
```

### Running
```=1
make aart
```

### i18N
+ AART provide i18n language system, see the [documentation](./AART_project/src/gettextDocument.md) for detail

### System requirements
+ see [system requirements](./systemRequiremnts.md) file for detail

### Commit hooks
+ This github repository had installed **pre-commit hook** and **commit-msg hook**, please install *pycodestyle* by `sudo pip3 install pycodestyle`. And install *autopep8* by `sudo pip3 install --upgrade autopep8`. Enable commit hooks by `make`, it will show something like `Git commit hooks are installed successfully.`

### Format code
+ Once you installed Commit hooks, format each python code by *autopep8*
usage:
```=1
autopep8 --in-place --global-config ~/.config/pep8 AART_project/src/main.py
```

### Author
+ [ambersun1234](https://github.com/ambersun1234)
+ [louisme87](https://github.com/louisme87)

### Contributors
+ [Fofo](https://github.com/jr00138017)
+ [s1123527](https://github.com/s1123527)
+ [snowmintowo](https://github.com/snowmint)
+ [wayne6172](https://github.com/wayne6172)
+ u10506106@ms.ttu.edu.tw
+ u10506107@ms.ttu.edu.tw
+ u10506125@ms.ttu.edu.tw
+ u10506131@ms.ttu.edu.tw
+ u10506123@ms.ttu.edu.tw
+ u10506151@ms.ttu.edu.tw

### License
+ This project is licensed under other license - see the [Other License](./LICENSE) file for detail
