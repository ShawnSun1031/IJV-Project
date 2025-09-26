install-apt-pkg:
	sudo apt update
	sudo apt install -y cmake git g++ gcc

install-pmcx:
	make install-apt-pkg
	bash scripts/install_pmcx.sh