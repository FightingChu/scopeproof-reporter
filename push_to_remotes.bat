@echo off
setlocal
cd /d "%~dp0"
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 goto not_repo
for /f "delims=" %%B in ('git rev-parse --abbrev-ref HEAD') do set "BRANCH=%%B"
if "%BRANCH%"=="" goto no_branch
git remote get-url gitee >nul 2>&1
if errorlevel 1 git remote add gitee git@gitee.com:cwyay/scopeproof-reporter.git
git remote set-url gitee git@gitee.com:cwyay/scopeproof-reporter.git
git remote get-url github >nul 2>&1
if errorlevel 1 git remote add github git@github.com:FightingChu/scopeproof-reporter.git
git remote set-url github git@github.com:FightingChu/scopeproof-reporter.git
git add -A
git diff --cached --quiet
if errorlevel 1 goto commit_changes
goto push_gitee

:commit_changes
git commit -m "chore: prepare remote push"
if errorlevel 1 goto commit_error

:push_gitee
git push -u gitee "%BRANCH%"
if errorlevel 1 goto gitee_error
git push -u github "%BRANCH%"
if errorlevel 1 goto github_error
echo Push completed for Gitee and GitHub.
goto end

:not_repo
echo This script must stay inside the scopeproof-reporter Git repository.
goto end

:no_branch
echo Git could not determine the current branch. Create an initial commit and retry.
goto end

:commit_error
echo Git commit failed. Check git status and configure user.name and user.email.
goto end

:gitee_error
echo Gitee push failed. Add your public key to Gitee and run ssh -T git@gitee.com.
echo If asked to trust the host fingerprint, enter yes and retry this script.
echo If SSH port 22 is blocked, configure a reachable SSH endpoint allowed by Gitee.
goto end

:github_error
echo GitHub push failed. Add your public key to GitHub and run ssh -T git@github.com.
echo If asked to trust the host fingerprint, enter yes and retry this script.
echo If port 22 is blocked, add these lines to .ssh\config and retry.
echo Host github.com
echo HostName ssh.github.com
echo Port 443
echo User git
goto end

:end
echo.
pause
endlocal
