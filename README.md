# Navegação Autônoma de Robô 2D com Stage e ROS 2

Projeto de navegação autônoma de um robô móvel 2D utilizando **Stage, ROS 2 e LiDAR**, incluindo percepção do ambiente e desvio de obstáculos com orientação até um destino predefinido.

O projeto foi desenvolvido inicialmente como atividade acadêmica e documentado posteriormente para registrar a experiência prática com ROS 2 e permitir a reprodução do ambiente.

---

## Sobre o projeto

O objetivo foi desenvolver um controlador capaz de movimentar um robô de forma autônoma dentro de um ambiente 2D simulado.

O robô deve:

- identificar sua posição e orientação;
- determinar a direção de um destino;
- utilizar o LiDAR para identificar obstáculos;
- decidir para qual lado desviar;
- continuar procurando o objetivo após o desvio;
- parar ao atingir a região de destino.

O destino utilizado durante os testes foi aproximadamente:

```text
X = 5.0
Y = 4.0
```

A solução implementada utiliza uma estratégia de **navegação reativa**.  
Não foi utilizado um planejador global de trajetória, como Nav2, A* ou Dijkstra.

O robô toma decisões continuamente a partir da sua posição, orientação e das leituras do LiDAR.

---

## Tecnologias utilizadas

- Ubuntu 24.04
- ROS 2 Jazzy
- Python 3
- Stage
- stage_ros2
- LiDAR simulado
- `rclpy`
- `geometry_msgs`
- `sensor_msgs`
- `nav_msgs`
- colcon
- rosdep
- Git e GitHub

---

## Arquitetura da solução

O controlador utiliza principalmente três tópicos ROS 2:

```text
/base_scan
/ground_truth
/cmd_vel
```

A comunicação pode ser representada de forma simplificada assim:

```text
                   +------------------+
/base_scan ------->|                  |
                   | stage_controller |-------> /cmd_vel -------> Stage
/ground_truth ---->|                  |
                   +------------------+
                           |
                           |
                    tomada de decisão
```

### `/base_scan`

Fornece as leituras do sensor LiDAR.

### `/ground_truth`

Fornece a posição e a orientação do robô no ambiente simulado.

### `/cmd_vel`

Recebe os comandos de velocidade linear e angular calculados pelo controlador.

---

# Como reproduzir o projeto

Este passo a passo considera que o **ROS 2 Jazzy já está instalado no Ubuntu 24.04**.

---

## 1. Criar o workspace

Crie a pasta `src`:

```bash
mkdir -p ~/stage_ros2_ws/src
```

Entre na raiz do workspace:

```bash
cd ~/stage_ros2_ws
```

A estrutura inicial será:

```text
stage_ros2_ws/
└── src/
```

Quando o workspace for compilado pelo `colcon`, também serão criadas automaticamente:

```text
stage_ros2_ws/
├── build/
├── install/
├── log/
└── src/
```

As funções principais dessas pastas são:

- `src/` → códigos-fonte;
- `build/` → arquivos utilizados na compilação;
- `install/` → resultado dos pacotes compilados;
- `log/` → registros das compilações.

Os três projetos utilizados ficarão dentro de `src`:

```text
src/
├── Stage/
├── stage_ros2/
└── stage_controller/
```

---

## 2. Baixar o Stage

Entre em:

```bash
cd ~/stage_ros2_ws/src
```

Clone o Stage:

```bash
git clone https://github.com/tuw-robotics/Stage.git
```

O **Stage** é responsável pela simulação 2D do ambiente, do robô e dos sensores.

Repositório:

```text
https://github.com/tuw-robotics/Stage
```

---

## 3. Baixar o stage_ros2

Ainda dentro de:

```text
~/stage_ros2_ws/src
```

clone a versão do `stage_ros2` para ROS 2 Jazzy:

```bash
git clone -b jazzy https://github.com/tuw-robotics/stage_ros2.git
```

O `stage_ros2` funciona como interface entre o simulador Stage e o ROS 2.

Repositório:

```text
https://github.com/tuw-robotics/stage_ros2
```

---

## 4. Baixar este controlador

Ainda dentro da pasta `src`:

```bash
cd ~/stage_ros2_ws/src
```

clone este repositório utilizando o nome `stage_controller`:

```bash
git clone https://github.com/anickssm/navegacao-autonoma-stage-ros2.git stage_controller
```

Ao final, a estrutura esperada será:

```text
stage_ros2_ws/
└── src/
    ├── Stage/
    ├── stage_ros2/
    └── stage_controller/
```

O pacote `stage_controller` contém o controlador desenvolvido neste projeto.

---

## 5. Instalar as dependências

Atualize os pacotes do Ubuntu:

```bash
sudo apt update
```

Instale as ferramentas utilizadas:

```bash
sudo apt install git python3-colcon-common-extensions python3-rosdep ros-jazzy-ackermann-msgs
```

Caso o `rosdep` ainda não tenha sido inicializado nessa instalação:

```bash
sudo rosdep init
```

Atualize sua base:

```bash
rosdep update
```

Entre na raiz do workspace:

```bash
cd ~/stage_ros2_ws
```

Instale as dependências:

```bash
rosdep install --from-paths src --ignore-src -r -y
```

Se tudo estiver correto, deverá aparecer uma mensagem semelhante a:

```text
All required rosdeps installed successfully
```

---

## 6. Compilar

Na raiz do workspace:

```bash
cd ~/stage_ros2_ws
```

Carregue o ROS 2:

```bash
source /opt/ros/jazzy/setup.bash
```

Compile:

```bash
colcon build --symlink-install
```

Depois carregue os pacotes compilados:

```bash
source install/setup.bash
```

---

# Executando o projeto

São utilizadas duas abas do terminal.

---

## Terminal 1 - Simulador

Entre no workspace:

```bash
cd ~/stage_ros2_ws
```

Carregue o ambiente:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

Abra o cenário `cave`:

```bash
ros2 launch stage_ros2 demo.launch.py world:=cave use_stamped_velocity:=false
```

O **Stage** e o **RViz** devem ser inicializados.

Deixe esse terminal executando.

---

## Terminal 2 - Controlador

Abra uma segunda aba do terminal.

Entre no workspace:

```bash
cd ~/stage_ros2_ws
```

Carregue novamente o ambiente:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

Execute:

```bash
ros2 run stage_controller stage_controller
```

O robô começará a navegar de forma autônoma.

---

## Atalhos úteis no terminal

No terminal do Ubuntu:

```text
Ctrl + Shift + C  → copiar
Ctrl + Shift + V  → colar
Ctrl + C          → interromper o programa em execução
```

`Ctrl + C` pode ser utilizado para parar tanto o controlador quanto o simulador.

Ao abrir uma nova aba do terminal, é necessário carregar novamente o ambiente ROS 2:

```bash
source /opt/ros/jazzy/setup.bash
source ~/stage_ros2_ws/install/setup.bash
```

---

# Funcionamento do controlador

## Posição do robô

O controlador recebe a posição do robô através de:

```text
/ground_truth
```

São utilizadas principalmente as coordenadas:

```text
X
Y
```

A posição atual é comparada continuamente com o destino:

```text
X = 5.0
Y = 4.0
```

---

## Orientação e yaw

A orientação fornecida pelo ROS 2 utiliza quaternion.

Para facilitar o controle em um ambiente 2D, o quaternion é convertido para o ângulo **yaw**.

O yaw indica aproximadamente para onde o robô está apontando:

```text
yaw = 0       → direita
yaw = 1.57    → cima
yaw = 3.14    → esquerda
yaw = -1.57   → baixo
```

O controlador calcula:

```text
direção do objetivo
        -
direção atual do robô
        =
erro de orientação
```

Esse erro é utilizado para decidir para qual lado o robô deve girar.

---

## Percepção utilizando LiDAR

As informações do LiDAR chegam pelo tópico:

```text
/base_scan
```

As leituras são separadas em três regiões:

```text
               FRENTE
                 ↑
           \     |     /
            \    |    /

       ESQUERDA  ROBÔ  DIREITA
```

O controlador analisa:

- distância frontal;
- distância do lado esquerdo;
- distância do lado direito.

Quando encontra um obstáculo, compara o espaço disponível dos dois lados para escolher uma direção de desvio.

---

# Estratégia de navegação

A lógica utilizada pode ser resumida assim:

```text
Qual é minha posição?
         ↓
Onde está o destino?
         ↓
Para qual direção devo apontar?
         ↓
Existe obstáculo?
       ↙      ↘
     não      sim
      ↓        ↓
seguir em   analisar
direção ao  LiDAR
objetivo      ↓
           escolher
             lado
              ↓
            desviar
              ↓
       procurar novamente
          o objetivo
```

Quando o caminho está livre, o robô tenta manter sua orientação em direção ao destino.

Quando existe um obstáculo, entra em um modo de desvio.

Após encontrar novamente espaço livre, retoma a orientação para o destino.

Essa estratégia é reativa e não utiliza um mapa previamente calculado ou planejamento global de trajetória.

---

# Chegada ao destino

O robô não precisa posicionar exatamente seu centro sobre a coordenada final.

Foi definida uma região de tolerância ao redor do objetivo.

Quando entra nessa região, o controlador envia:

```text
velocidade linear = 0
velocidade angular = 0
```

e o robô permanece parado.

Também foi implementada uma condição de reativação.

Caso o robô seja deslocado manualmente para longe do objetivo depois de concluir a missão, o controlador detecta novamente a distância e retoma automaticamente a navegação.

---

# Resultados

Durante os testes realizados, o robô conseguiu:

- navegar autonomamente no cenário;
- obter sua posição e orientação;
- calcular a direção de um destino predefinido;
- utilizar o LiDAR para perceber obstáculos;
- analisar obstáculos à frente, esquerda e direita;
- escolher uma direção de desvio;
- retomar a busca pelo destino após o desvio;
- parar automaticamente ao atingir a região objetivo;
- reiniciar a missão quando deslocado novamente.

---

# Limitações da solução

A estratégia utilizada é propositalmente simples e reativa.

O robô não possui:

- planejamento global de trajetória;
- construção de mapa;
- algoritmo A*;
- algoritmo Dijkstra;
- Nav2;
- SLAM.

Por esse motivo, dependendo da geometria do ambiente, o comportamento de desvio pode não representar o caminho mais curto e podem ocorrer correções sucessivas de direção.

O objetivo deste projeto foi experimentar os conceitos fundamentais de:

```text
sensoriamento
     ↓
percepção
     ↓
tomada de decisão
     ↓
controle
```

utilizando ROS 2 em um robô móvel simulado.

---

# Experiência adquirida

O desenvolvimento deste projeto proporcionou experiência prática com:

- criação e organização de um workspace ROS 2;
- criação de um pacote Python utilizando `ament_python`;
- publishers e subscribers;
- mensagens `Twist`;
- mensagens `LaserScan`;
- mensagens de odometria;
- tópicos ROS 2;
- processamento de dados de LiDAR;
- orientação utilizando yaw;
- controle de velocidade linear e angular;
- simulação utilizando Stage;
- integração entre Stage e ROS 2;
- compilação com colcon;
- gerenciamento de dependências com rosdep;
- versionamento utilizando Git e GitHub.

---

## Estrutura principal do pacote

```text
stage_controller/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
├── stage_controller/
│   ├── __init__.py
│   └── stage_controller.py
└── test/
```

O arquivo principal do controlador é:

```text
stage_controller/stage_controller.py
```
