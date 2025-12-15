
import subprocess
import os
import time

QWEN_CMD = ["qwen"]

AGENTS_DIR = "agents"

def load_agent(name):
    with open(os.path.join(AGENTS_DIR, f"{name}.txt"), "r") as f:
        return f.read()

def call_qwen(system_prompt, user_prompt):
    prompt = f"{system_prompt}\n\nTAREFA:\n{user_prompt}"

    process = subprocess.Popen(
        QWEN_CMD,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        output, _ = process.communicate(prompt, timeout=120)
    except subprocess.TimeoutExpired:
        process.kill()
        return "ERRO: timeout"

    return output.strip()

def run(task, max_iter=5):
    architect = load_agent("architect")
    developer = load_agent("developer")
    qa = load_agent("qa")
    security = load_agent("security")
    reviewer = load_agent("reviewer")

    context = {"task": task}

    for i in range(max_iter):
        print(f"\nITERACAO {i+1}")

        arch = call_qwen(architect, context["task"])
        print("\n[ARCHITECT]\n", arch)

        code = call_qwen(developer, arch)
        print("\n[DEVELOPER]\n", code)

        qa_out = call_qwen(qa, code)
        print("\n[QA]\n", qa_out)

        sec_out = call_qwen(security, code)
        print("\n[SECURITY]\n", sec_out)

        review_input = f"Codigo:\n{code}\n\nQA:\n{qa_out}\n\nSecurity:\n{sec_out}"

        decision = call_qwen(reviewer, review_input)
        print("\n[REVIEWER]\n", decision)

        if "APROVADO" in decision:
            print("\nFINALIZADO")
            return

        context["task"] += f"\n\nCorrigir:\n{qa_out}\n{sec_out}"
        time.sleep(1)

    print("\nLimite de iteracoes atingido")

if __name__ == "__main__":
    task = input("O que deseja construir?\n")
    run(task)
