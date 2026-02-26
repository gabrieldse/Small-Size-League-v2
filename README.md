# SSL-EL

source venv/bin/activate

git checkout -b feature/[nome-da-funcionalidade]

git add .
git commit -m "feat: descrição clara do que foi feito"

git push -u origin feature/[nome-da-funcionalidade]



Type,Use Case,Example
feat,A new feature for the robot or AI.,feat: add open loop circular dribbling
fix,"A bug fix (logic, math, or crash).",fix: correct robot orientation wrap-around
refactor,Code change that neither fixes a bug nor adds a feature.,refactor: simplify vector math in navigation
style,"Changes that do not affect the meaning of the code (white-space, formatting).",style: run clang-format on vision module
test,Adding missing tests or correcting existing tests.,test: add unit tests for geometry utils
docs,Documentation only changes.,docs: update onboarding guide for new members
chore,"Updating build tasks, package manager configs, etc.",chore: add pre-commit hooks to repo
perf,A code change that improves performance.,perf: optimize collision detection loop
