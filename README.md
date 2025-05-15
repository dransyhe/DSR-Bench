
Environment:

`conda env create -f environment.yml` to generate a conda environment called `NLGraph`

First set your openai key `OEPNAI_API_KEY` (and openai organization `OPENAI_ORGANIZATION` optionally):
```
$env:OPENAI_API_KEY="your openai api key" # for Windows powershell
export OPENAI_API_KEY="your openai api key" # for Linux
export ANTHROPIC_API_KEY="your anthropic api key" 
export LLAMA_API_KEY="your llama api key"
export GEMINI_API_KEY="your gemini api key"
export DEEPSEEK_API_KEY="your deepseek api key"
export GOOGLE_PROJECT_ID="your google project id"
export GOOGLE_BUCKET_ID="your google bucket id"
```
then run the evaluation code for a specific task:
```
python -m evaluation.<type>.<operation> 
```

optionally for more controls:
```
python -m evaluation.<type>.<operation> --model <name of LM> --mode <difficulty_mode> --prompt <prompting technique> --T <temperature> --token <max number of token> --SC <whether to use self-consistency> --SC_num <sampling number for SC>
```

e.g.
```
python -m evaluation.array.access --prompt CoT
```
