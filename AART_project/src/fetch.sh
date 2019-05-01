IFS=$'\n'
id=()
usb=($(lsusb | awk -F "ID " '{print $2}'))
byid=($(ls -al /dev/v4l/by-id | cut -c42-))

for i in "${byid[@]}"
	do
		if [[ "${i}" = "." ]] || [[ "${i}" = ".." ]]; then
			continue
		fi
		first=$(echo ${i} | awk -F ' ->' '{print $1}')
		temp=$(echo ${first} | cut -d "-" -f2- | cut -d "-" -f-1 | tr "_" ":")
		temp2=$(echo ${i} | awk -F ' ->' '{print $2}' | cut -c13-)
		id=("${id[@]}" "${temp}_${temp2}")
	done

IFS='|'
echo -n "${id[*]}@${usb[*]}"