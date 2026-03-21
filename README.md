# Titans - Small Size League (SSL) - EL

Welcome to the Titans Small Size League (SSL) project repository! This codebase provides everything our robots need to play soccer. Our goal is to compete in CBR 2026.

## 📚 Documentation & Onboarding

For new members and detailed setup instructions, please start by reading our documentation online:
👉 **[SSL Onboarding & Documentation](https://gabrieldse.github.io/Small-Size-League-v2/)**

---

## 🚀 Quick Setup

Run the following commands to build and test the environment:
```sh
git clone git@github.com:gabrieldse/Small-Size-League-v2.git
cd Small-Size-League-v2
docker build .
docker compose run --rm --name my_ssl dev
xhost +local:docker
grSim # as a graphical test
```
