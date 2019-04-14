GIT_HOOKS := .git/hooks/applied
hook: ${GIT_HOOKS}

$(GIT_HOOKS):
	@bash ./scripts/install-git-hooks
	@echo

genpo: AART_project/src/config/configJSON.py \
		AART_project/src/device/device.py \
		AART_project/src/input/input.py \
		AART_project/src/main.py \
		AART_project/src/media/media.py \
		AART_project/src/output/output.py \
		AART_project/src/welcome/welcome.py
		@mkdir -p AART_project/src/locales
		pygettext -d base -o AART_project/src/locales/base.pot $^
		@mkdir -p AART_project/src/locales/tw/LC_MESSAGES
		@cp AART_project/src/locales/base.pot AART_project/src/locales/tw/LC_MESSAGES/base.po

genmo: AART_project/src/locales/tw/LC_MESSAGES/base.po
	msgfmt -o AART_project/src/locales/tw/LC_MESSAGES/base.mo base
