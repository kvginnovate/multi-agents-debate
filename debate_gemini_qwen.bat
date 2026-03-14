@echo off
setlocal enabledelayedexpansion

:: ============================================================================
::  GEMINI vs QWEN DEBATE - Multi-Agent Debate System
:: ============================================================================
:: 
:: Usage: 
::   debate_gemini_qwen.bat [topic]
::   debate_gemini_qwen.bat
::
:: Requirements:
::   - Gemini CLI installed (npm install -g @google/gemini-cli)
::   - Qwen CLI installed (npm install -g @anthropic/qwen-cli)
::   - API keys set in environment or settings files
:: ============================================================================

echo.
echo ============================================================================
echo   GEMINI vs QWEN DEBATE
echo ============================================================================
echo.

:: Get topic from command line or prompt user
if "%~1"=="" (
    set /p TOPIC="Enter debate topic: "
) else (
    set "TOPIC=%*"
)

if "%TOPIC%"=="" (
    echo Error: Topic cannot be empty!
    exit /b 1
)

echo Topic: %TOPIC%
echo.

:: Set number of rounds (default 3 for batch mode)
set ROUNDS=3

echo Rounds: %ROUNDS%
echo.
echo ============================================================================
echo.

:: Create temp files for storing arguments
set TEMP_DIR=%TEMP%\debate_%RANDOM%
mkdir "%TEMP_DIR%" 2>nul

set GEMINI_ARG=%TEMP_DIR%\gemini_arg.txt
set QWEN_ARG=%TEMP_DIR%\qwen_arg.txt

:: ============================================================================
::  OPENING STATEMENTS
:: ============================================================================
echo --- ROUND 1: Opening Statements ---
echo.

echo **Gemini (Affirmative):**
echo.
gemini -y -p "You are debating the topic: \"%TOPIC%\". You are taking the AFFIRMATIVE side (supporting the topic). Present logical arguments with evidence and reasoning. Be concise but persuasive. Keep your response under 200 words. Start your response directly with your argument." > "%GEMINI_ARG%"
type "%GEMINI_ARG%"
set GEMINI_PREV=
for /f "delims=" %%a in ('type "%GEMINI_ARG%"') do set GEMINI_PREV=!GEMINI_PREV! %%a
echo.

echo **Qwen (Negative):**
echo.
qwen -y -p "You are debating the topic: \"%TOPIC%\". You are taking the NEGATIVE side (opposing the topic). Present logical arguments with evidence and reasoning. Be concise but persuasive. Keep your response under 200 words. Start your response directly with your argument." > "%QWEN_ARG%"
type "%QWEN_ARG%"
set QWEN_PREV=
for /f "delims=" %%a in ('type "%QWEN_ARG%"') do set QWEN_PREV=!QWEN_PREV! %%a
echo.

:: ============================================================================
::  DEBATE ROUNDS
:: ============================================================================
for /L %%i in (2,1,%ROUNDS%) do (
    echo --- ROUND %%i: Rebuttals ---
    echo.

    echo **Gemini (rebutting Qwen):**
    echo.
    gemini -y -p "You are debating the topic: \"%TOPIC%\". You are taking the AFFIRMATIVE side. Qwen's previous argument was: \"!QWEN_PREV!\". Rebut their points and strengthen your position with logical arguments and evidence. Keep your response under 200 words. Start your response directly with your argument." > "%GEMINI_ARG%"
    type "%GEMINI_ARG%"
    set GEMINI_PREV=
    for /f "delims=" %%a in ('type "%GEMINI_ARG%"') do set GEMINI_PREV=!GEMINI_PREV! %%a
    echo.

    echo **Qwen (rebutting Gemini):**
    echo.
    qwen -y -p "You are debating the topic: \"%TOPIC%\". You are taking the NEGATIVE side. Gemini's previous argument was: \"!GEMINI_PREV!\". Rebut their points and strengthen your position with logical arguments and evidence. Keep your response under 200 words. Start your response directly with your argument." > "%QWEN_ARG%"
    type "%QWEN_ARG%"
    set QWEN_PREV=
    for /f "delims=" %%a in ('type "%QWEN_ARG%"') do set QWEN_PREV=!QWEN_PREV! %%a
    echo.
)

:: ============================================================================
::  CLOSING STATEMENTS
:: ============================================================================
echo --- CLOSING STATEMENTS ---
echo.

echo **Gemini (Closing):**
echo.
gemini -y -p "You are debating the topic: \"%TOPIC%\". You are taking the AFFIRMATIVE side. Provide a strong closing statement summarizing your key points and why your position is stronger. Keep your response under 150 words." > "%GEMINI_ARG%"
type "%GEMINI_ARG%"
echo.

echo **Qwen (Closing):**
echo.
qwen -y -p "You are debating the topic: \"%TOPIC%\". You are taking the NEGATIVE side. Provide a strong closing statement summarizing your key points and why your position is stronger. Keep your response under 150 words." > "%QWEN_ARG%"
type "%QWEN_ARG%"
echo.

:: ============================================================================
::  CLEANUP
:: ============================================================================
echo ============================================================================
echo   DEBATE COMPLETE!
echo ============================================================================
echo.

:: Cleanup temp files
del "%GEMINI_ARG%" 2>nul
del "%QWEN_ARG%" 2>nul
rmdir "%TEMP_DIR%" 2>nul

endlocal
