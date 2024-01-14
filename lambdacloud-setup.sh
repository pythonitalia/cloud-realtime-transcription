sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
  xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
sudo apt install zlib1g zlib1g-dev libssl-dev libbz2-dev libsqlite3-dev
sudo apt install libssl-dev

git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.13.1
source "$HOME/.asdf/asdf.sh"

asdf plugin-add python
asdf install python 3.11.7
asdf global python 3.11.7

LAMBDA_REPO=$(mktemp) && \
wget -O${LAMBDA_REPO} https://lambdalabs.com/static/misc/lambda-stack-repo.deb && \
sudo dpkg -i ${LAMBDA_REPO} && rm -f ${LAMBDA_REPO} && \
sudo apt-get update && \
sudo apt-get --yes upgrade && \
sudo apt-get install --yes --no-install-recommends lambda-server && \
sudo apt-get install --yes --no-install-recommends nvidia-headless-470 && \
sudo apt-get install --yes --no-install-recommends lambda-stack-cuda

sudo apt-get install portaudio19-dev python-all-dev python3-all-dev

curl -sSL https://pdm-project.org/install-pdm.py | python3 -

cd server && pdm install
cd client && pdm install
