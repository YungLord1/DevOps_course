### ДЗ #6 (k8s. основы)

Доброго времени суток! Спасибо большое за лекцию, было очень интересно послушать про инструмент, о котором мало знаю. И сначала вроде боялся k8s, но ПОКА ЧТО после этой домашки мне он понравился :) Было довольно просто и интересно, больше всего проблем больших возникало из-за прокси и рейт лимита. Ниже описал все, что сделал по пунктам 

## Для проверки моего дз могу ли попросить прислать pub key для подключения по SSH? Если да, то будет замечательно, я его добавлю в authorized_keys

---

## Процесс развертывания и отладки

### Проверка системных настроек
Проверил вывод
```bash
sysctl net.bridge.bridge-nf-call-iptables net.bridge.bridge-nf-call-ip6tables net.ipv4.ip_forward
```
Ожидаемый результат:
# net.bridge.bridge-nf-call-iptables = 1
# net.bridge.bridge-nf-call-ip6tables = 1
# net.ipv4.ip_forward = 1
Вывело все то же самое на всех ВМ

---

### Инициализация кластера
запускаю кубер командой
```bash
kubeadm init \
  --apiserver-advertise-address=10.184.0.43 \
  --pod-network-cidr=192.168.0.0/16 \
  --service-cidr=10.96.0.0/12
```
добавил флаг `--apiserver-advertise-address=10.184.0.43` для того чтобы в будущем, если получится успеется или так будет надо - использовать несколько сетевых интерфейсов
1. Ошибка что запустил без судо
2. Ошибка что есть 2 сокета крио и контейнерди, посмотрел что контейнерди не используется - остановил его через systemctl stop + disabled

control plane инициализировался успешно, выполнил 3 базовых команды которые он выдал в конце для того, чтобы я мог усправлять кластером с помощью kubectl не только от root'а
```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

---

### Добавление воркеров
Далее на воркерах отлкючил SWAP командой `swapoff -a` и удалил containerd
и добавил воркеры к мастер через `kubeadm join`

После добавления выполнил get nodes на мастере и там был только мастер и воркер. Я понял, что хостнейм у обоих воркеров одинаковый, поэтому на мастере выполнил `kubectl delete node worker`, на воркерах сбросил настройки kubeadm, переименовал воркеров в worker1 и worker2 и добавил их заново

выполнил `kubectl get nodes` и появились оба воркера со статусом нот реди

![kubectl get nodes](images/k8s/getnodes.jpg)

---

### Установка Calico
далее создал новый неймспейс tigera-operator и запустился одноименный под командой 
```bash
kubectl create -f [https://raw.githubusercontent.com/projectcalico/calico/v3.25.2/manifests/tigera-operator.yaml](https://raw.githubusercontent.com/projectcalico/calico/v3.25.2/manifests/tigera-operator.yaml)
```
через `kubectl get ns` проверил и в правду, появился нс tigera-operator

командой `kubectl get all -n tigerA-operator` (в презентации очепятка) посмотрел на под, у которого был статус раннинг

Кстати в оф доках калико есть еще одна команда `kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.25.2/manifests/operator-crds.yml`, она нужна для более новых версий калико, для нашей версии 3.25.2 это расширение не потребуется

Далее я скачал файл конфигурации калико командой 
```bash
curl -O [https://raw.githubusercontent.com/projectcalico/calico/v3.25.2/manifests/custom-resources.yaml](https://raw.githubusercontent.com/projectcalico/calico/v3.25.2/manifests/custom-resources.yaml)
```
Именно для этого шага, чтобы я его не перенастраивал, я заранее посмотрел документацию калико и в поле `ipPools: cidr:` этого файла указано `192.168.0.0/16`, та подсеть, которую я указал при `kubeadm init`

Далее применил файл командой `kubectl create -f custom-resources.yaml` и создался манифест для установки калико

командой `watch kubectl get tigerastatus` посмотрел статус available у apiserver'а и калико, он True!

![get tigerastatus](images/k8s/get_tigera.jpg)

После применл команду `get nodes` и все ноды были в статусе Ready!
![kubectl get nodes](images/k8s/getnodes.jpg)

---

### Решение проблемы с пингом в подах
После запуска команды с лекции `kubectl run -ti --tty testpod --image=busybox -- sh` захожу в контейнер и пытаюсь выполнить `ping 8.8.8.8`
Но вылетает ошибка permission denied(are you root)
Проверил Id, я рут) попробовал выполнить команду `nslookup google.com` чтобы проверить может ли контейнер выйти в сеть, все работает

Копнул глубже и посмотрел, что с версии 1.18 крио контейнеры запускаются без `NET_RAW` и `SYS_CHROOT` capabilities, `SYS_CHROOT` Нам сейчас особо не надо, а вот `NET_RAW` Нужен для пинга
Поэтому берем файлик, который я создавал при предыдущей домашке, `99-default.conf`, У меня лежит 3 файла конфигурации, 1 дефолт, второй лишний, но в любом случае 99 читается последним и перекроет все другие. Туда добавляю капабилити `NET_RAW`
![capabilities NET_RAW](images/k8s/NETRAW.jpg)

Обязательно перезапускаю крио командой `sudo systemctl restart crio`
создаю снова под, пингую - не работает
попробовал засунуть в другие файлы конфигурации - не работает
Потом я почитал статьи по куберу и до меня дошло, что я все конфиги менял на мастере, а поды ведь создаются на воркерах, а на них я ничего не менял
поменял конфигурации в файле `99-default.conf` на воркере1 и воркере2, перезапустил крио командой `systemctl restart crio`, создал контейнер, прописал пинг и все работает!
![ping 8.8.8.8 busybox](images/k8s/pingBUSY.jpg)

upd. Поймал рейт лимит по скачиванию busybox, использовал зеркало чтобы проверить пинг, также все работало 
```bash
kubectl run testpod -it --rm --image=mirror.gcr.io/library/busybox:latest --image-pull-policy=IfNotPresent -- sh
```







---

### Задание со звездочкой: Ansible Playbook

Наломав дров вручную и зная все ошибки, я приступил к автоматизации. Для тестов использовал новую ВМ в дата-центре Германии (меньше проблем с прокси).

Добавил публичный ключ в `authorized_keys`, прописал IP и запустил готовый плейбук из прошлого ДЗ:
```bash
ansible-playbook playbook.yml -l tests
```
Результат положительный!
![playbook OLD](images/k8s/playbookfirst.jpg)

### Новая роль: cluster_up
Я создал роль cluster_up, структура которой включает:

1. master.yml — инициализация control-plane, настройка kubeconfig и установка сетевого плагина.

2. workers.yml — подготовка воркер-нод и присоединение к кластеру.

3. main.yml — логика подключения этапов.

## Ошибки, которые я исправил в процессе:

1. Handler Error: Ошибка restart crio not found. Исправил, добавив отдельную таску через ansible.builtin.systemd в handlers/main.yml.

2. Calico Validation: При установке Calico возникла ошибка валидации, пришлось добавить флаг --validate=false в таску.

3. Proxy Issue: При скачивании манифестов прокси нужен, а при запросах kubectl к API — мешает. Переписал логику использования окружения в YAML, разделив эти процессы.

4. Path Error: Исправил опечатку в пути к файлу workers.yml.

Плейбук прошел успешно на локальных воркерах. Для проверки сети запустил под через зеркало (чтобы обойти рейт-лимиты):

```Bash
kubectl run testpod -it --rm --image=mirror.gcr.io/library/busybox:latest --image-pull-policy=IfNotPresent -- sh
```
Флаг --rm сразу удаляет под после выхода. Пинг прошел успешно!
![ping 8.8.8.8 busybox mirror](images/k8s/pingmirror.jpg)
---






### Настройка Dashboard
Для добавления аддона дашборда сначала пробовал Helm по официальному гайду, но получил 404. Решил разворачивать через манифесты.

## Развертывание подов:

```Bash
kubectl apply -f [https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml](https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml)
```
**Создание админа**:
Создал папку dashboard и файл dashboard-admin.yaml. Применил его (предварительно поправив структуру YAML в блоке spec). Вытащил токен для входа:

```Bash
kubectl -n kubernetes-dashboard create token admin-user
```

**Настройка доступа:**
Отредактировал сервис:

```Bash
kubectl -n kubernetes-dashboard edit service kubernetes-dashboard
```
Поменял type: ClusterIP на type: NodePort.

**Решение проблем с образами:**
По айпи не заходило из-за того, что образы не скачивались. Решил проблему через ручной pull из зеркала и правку deployment:

```Bash
sudo crictl pull mirror.gcr.io/kubernetesui/dashboard:v2.7.0
sudo crictl pull mirror.gcr.io/kubernetesui/metrics-scraper:v1.0.8
```
Заменил image в конфиге: ``` kubectl edit deployment kubernetes-dashboard -n kubernetes-dashboard.```

**Все заработало! Подтверждающие скриншоты ниже:**

![dashboard nodes](images/k8s/dashnodes.jpg)

![dashboard pods](images/k8s/dashpods.jpg)

## Спасибо за проверку, хорошего дня!

![Я, когда понял, что внешняя ВМ не будет пинговать ВМки YADRO](https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcHRxcnprMG93ZmJhZ29yaTQ3YTYzNGhtNzAxank3ZndyOHlyMHRzMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/zOvBKUUEERdNm/giphy.gif)
# Я, когда спустя час понял, что внешняя ВМ не сможет пинговать ВМки YADRO