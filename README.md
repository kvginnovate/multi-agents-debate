# Multi-Agent Debate (MAD) Framework

This repository contains the source code and data for the paper "[MAD: Multi-Agent Debate : Multi-Agent Debate with Large Language Models](https://arxiv.org/abs/2303.17434)".

## Overview

Multi-Agent Debate (MAD) is a framework that encourages multiple agents to debate their answers and discuss their perspectives to reach a better consensus. This framework is particularly effective for tasks that require complex reasoning and multiple perspectives.

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kvginnovate/multi-agents-debate.git
    cd multi-agents-debate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the debate:**
    Check out the [QUICKSTART.md](QUICKSTART.md) for detailed instructions on running debates between Gemini and Qwen.

## Supported Models

-   **OpenAI GPT models** (GPT-3.5, GPT-4, GPT-4o, etc.)
-   **Google Gemini** (Gemini Pro, Gemini 1.5 Pro/Flash, etc.)
-   **Alibaba Qwen** (Qwen Turbo, Plus, Max, etc.)

## Project Structure

-   `code/`: Core implementation of the MAD framework.
-   `data/`: Datasets and debate process logs.
-   `imgs/`: Visualizations and framework diagrams.
-   `scripts/`: Batch scripts and CLI tools.

## Citation

If you find this work useful, please cite our paper:

```bibtex
@article{liang2023encouraging,
  title={Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate},
  author={Liang, Tian and He, Zhiwei and Jiao, Wenxiang and Wang, Xing and Wang, Yan and Wang, Rui and Yang, Zhaopeng and Tu, Zhaopeng and Shi, Shuming},
  journal={arXiv preprint arXiv:2303.17434},
  year={2023}
}
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
