GIT_HOOKS := .git/hooks/applied
SRC := AART_project/src
LCTW := AART_project/src/locales/tw/LC_MESSAGES
LCEN := AART_project/src/locales/en/LC_MESSAGES

hook: ${GIT_HOOKS}

aart: 
	@cd AART_project/src && python3 main.py || exit 1

$(GIT_HOOKS):
	@bash ./scripts/install-git-hooks
	@echo

genenpo: ${SRC}/config/configJSON.py \
		${SRC}/device/device.py \
		${SRC}/input/input.py \
		${SRC}/main.py \
		${SRC}/media/media.py \
		${SRC}/output/output.py \
		${SRC}/welcome/welcome.py
		@mkdir -p ${SRC}/locales
		pygettext3.5 -d base -o ${SRC}/locales/baseen.pot $^
		@mkdir -p ${LCEN}
		@sed -i 's/"Content-Type: text\/plain; charset=CHARSET\\n"/"Content-Type: text\/plain; charset=UTF-8\\n"/g' ${SRC}/locales/baseen.pot
		@cp ${SRC}/locales/baseen.pot ${LCEN}/base.po

genenmo: ${LCEN}/base.po
	msgfmt --statistics -D ${LCEN} -o ${LCEN}/base.mo base

gentwpo: ${SRC}/config/configJSON.py \
		${SRC}/device/device.py \
		${SRC}/input/input.py \
		${SRC}/main.py \
		${SRC}/media/media.py \
		${SRC}/output/output.py \
		${SRC}/welcome/welcome.py
		@mkdir -p ${SRC}/locales
		pygettext3.5 -d base -o ${SRC}/locales/basetw.pot $^
		@mkdir -p ${LCTW}
		@sed -i 's/"Content-Type: text\/plain; charset=CHARSET\\n"/"Content-Type: text\/plain; charset=UTF-8\\n"/g' ${SRC}/locales/basetw.pot
		@cp ${SRC}/locales/basetw.pot ${LCTW}/base.po

gentwmo: ${LCTW}/base.po
	msgfmt --statistics -D ${LCTW} -o ${LCTW}/base.mo base

.PHONY: gentwclean, genenclean

gentwclean: 
	rm -f ${SRC}/locales/basetw.pot
	rm -f ${LCTW}/base.*

genenclean:
	rm -f ${SRC}/locales/baseen.pot
	rm -f ${LCEN}/base.*
