# Publish to GitHub

The archive is repository-ready but does not include `.git`.

```bash
unzip distributed-workbench.zip
cd distributed-workbench
git init
git add .
git commit -m "feat: add distributed systems workbench"
gh repo create hjosugi/distributed-workbench --public --source=. --remote=origin --push
```

Before publishing, change the repository name and Go module paths if you want a different final URL. The supplied module paths assume `hjosugi/distributed-workbench`.
