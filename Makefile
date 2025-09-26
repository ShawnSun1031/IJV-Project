apt-pkg:
	sudo apt update
	sudo apt install -y cmake git g++ gcc

install-pmcx:
	bash scripts/install_pmcx.sh