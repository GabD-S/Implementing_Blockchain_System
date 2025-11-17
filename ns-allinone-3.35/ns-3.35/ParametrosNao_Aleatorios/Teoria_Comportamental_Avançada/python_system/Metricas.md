\documentclass[12pt]{article}

\usepackage{geometry}
\geometry{a4paper, margin=2cm}

\usepackage{titlesec}
\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}

\usepackage{setspace}
\onehalfspacing

\usepackage{indentfirst}

\begin{document}

\title{Plano de Métricas e Parâmetros para Avaliação de Redes Blockchain em Simulação}
\author{}
\date{}
\maketitle

\section{Métricas Essenciais a Serem Medidas}

\subsection{Performance e Capacidade}
\begin{itemize}
    \item medir throughput (tps).
    \item medir latência de confirmação e tempo de finalização.
    \item medir tempo de propagação de blocos e transações entre nós.
\end{itemize}

\subsection{Escalabilidade e Carga}
\begin{itemize}
    \item variar número de nós e medir impacto em tps e latência.
    \item variar carga de usuários e medir saturação da rede.
\end{itemize}

\subsection{Consistência e Segurança}
\begin{itemize}
    \item medir taxa de forks e blocos órfãos.
    \item medir impacto da fração de nós adversários no comportamento da rede.
    \item medir probabilidade de reorgs sob diferentes atrasos de propagação.
\end{itemize}

\subsection{Uso de Recursos}
\begin{itemize}
    \item medir uso de banda por nó.
    \item medir uso de cpu por nó.
    \item medir uso de memória por nó.
    \item medir custo por transação (quando aplicável).
\end{itemize}

\subsection{Qualidade de Serviço}
\begin{itemize}
    \item medir disponibilidade dos nós.
    \item medir tempo de recuperação após falhas.
\end{itemize}

\subsection{Descentralização}
\begin{itemize}
    \item medir distribuição do poder entre nós.
    \item medir concentração de stake ou capacidade.
\end{itemize}

\section{Parâmetros a Serem Variados}
\begin{itemize}
    \item número de nós.
    \item fração de nós adversários.
    \item taxa de geração de transações por usuário.
    \item latências de comunicação e jitter.
    \item tamanho do bloco ou limite de gas.
    \item intervalo de criação de blocos.
    \item banda disponível por nó.
    \item complexidade das operações de smart contract.
\end{itemize}

\section{Gráficos a Serem Produzidos}
\begin{itemize}
    \item gráfico tps versus número de nós.
    \item gráfico de latência versus taxa de transações.
    \item gráfico de taxa de forks versus latência de propagação.
    \item gráfico de uso de banda versus throughput.
    \item gráfico de uso de cpu versus carga.
    \item gráfico de disponibilidade versus tempo.
    \item cdf da latência de confirmação.
    \item heatmap de tamanho do bloco versus intervalo do bloco mostrando tps e latência.
\end{itemize}

\section{Integração com o Simulador}
\begin{itemize}
    \item instrumentar agentes para registrar timestamps de eventos.
    \item medir latências usando diferenças de timestamps.
    \item registrar número de transações confirmadas por janela de tempo.
    \item injetar atrasos de link controlados no simulador.
    \item simular comportamentos adversários conforme parâmetros.
    \item exportar logs em formato csv com colunas de tempo, nó, evento, latência, uso de recursos e estado.
\end{itemize}

\end{document}
