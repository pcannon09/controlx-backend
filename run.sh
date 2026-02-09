readonly LICENSE="ControlX-Backend (C) 2026 pcannon09
This program comes with ABSOLUTELY NO WARRANTY; for details type \`./run.sh --license\`.
This is free software, and you are welcome to redistribute it
under certain conditions; type \`./run.sh --license\` for details."

if [[ "$1" == "--license" ]]; then
	echo "$LICENSE"

else
	python -m main
fi
