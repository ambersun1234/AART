GIT_HOOKS := .git/hooks/applied
SRC := AART_project/src
LC := AART_project/src/locales/tw/LC_MESSAGES
hook: ${GIT_HOOKS}

$(GIT_HOOKS):
	@bash ./scripts/install-git-hooks
	@echo

genpo: ${SRC}/config/configJSON.py \
		${SRC}/device/device.py \
		${SRC}/input/input.py \
		${SRC}/main.py \
		${SRC}/media/media.py \
		${SRC}/output/output.py \
		${SRC}/welcome/welcome.py
		@mkdir -p ${SRC}/locales
		pygettext3.5 -d base -o ${SRC}/locales/base.pot $^
		@mkdir -p ${LC}
		@sed -i 's/"Content-Type: text\/plain; charset=CHARSET\\n"/"Content-Type: text\/plain; charset=UTF-8\\n"/g' ${SRC}/locales/base.pot
		@cp ${SRC}/locales/base.pot ${LC}/base.po

genmo: ${LC}/base.po
	msgfmt --statistics -D ${LC} -o ${LC}/base.mo base

.PHONY: genclean

genclean: 
	rm -f ${SRC}/locales/base.pot
	rm -f ${LC}/base.*
