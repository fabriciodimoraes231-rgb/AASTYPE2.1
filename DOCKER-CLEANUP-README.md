# 🧹 Script de Limpeza Docker

Script automatizado para limpar contêineres, processos zumbis e liberar portas ocupadas.

## 📋 O que o script faz:

1. ⏸️  **Para contêineres em execução** (opcional)
2. 🗑️  **Remove contêineres parados** (status: exited/created)
3. 🔍 **Identifica processos docker-proxy zumbis** nas portas:
   - 1883, 1884 (MQTT)
   - 9001, 9002 (WebSocket)
   - 8080, 8081 (HTTP)
   - 4840 (OPC UA)
   - 27017, 27018, 27019 (MongoDB)
4. 🌐 **Limpa redes não utilizadas**
5. 💾 **Remove volumes órfãos** (opcional - ⚠️ remove dados!)
6. 🖼️  **Remove imagens não utilizadas** (opcional)
7. 📊 **Mostra status final** do Docker

## 🚀 Como usar:

### Execução básica:
```bash
./cleanup-docker.sh
```

### Com privilégios de root (recomendado):
```bash
sudo ./cleanup-docker.sh
```

## ⚙️ Opções interativas:

O script vai perguntar antes de:
- Parar contêineres em execução
- Matar processos nas portas ocupadas
- Remover volumes (⚠️ **CUIDADO**: isso apaga dados!)
- Remover imagens não utilizadas

## 🔧 Quando usar:

### Antes de subir novos contêineres:
```bash
./cleanup-docker.sh
docker compose up -d
```

### Quando aparecer erro "port already in use":
```bash
./cleanup-docker.sh  # Limpa as portas
docker compose up -d  # Tenta novamente
```

### Limpeza completa do ambiente Docker:
```bash
sudo ./cleanup-docker.sh
# Responda "s" para todas as perguntas
```

## 🛡️ Segurança:

- ✅ Pede confirmação antes de ações destrutivas
- ✅ Requer sudo para matar processos do sistema
- ⚠️  **ATENÇÃO**: Remover volumes apaga dados persistentes!

## 📝 Exemplo de uso típico:

```bash
manuel@pc:~/projeto$ ./cleanup-docker.sh

🧹 Iniciando limpeza Docker...

❓ Deseja parar todos os contêineres em execução? (s/N): n
🗑️  Removendo contêineres parados...
✅ Contêineres removidos

🔍 Verificando processos docker-proxy nas portas...
⚠️  Porta 1883 ocupada pelos processos: 12345
   Deseja matar esses processos? (s/N): s
   ✅ Processos na porta 1883 eliminados

🌐 Limpando redes não utilizadas...
✅ Redes limpas

❓ Deseja remover volumes não utilizados? ⚠️  ISSO REMOVE DADOS! (s/N): n
⏭️  Volumes mantidos

❓ Deseja remover imagens não utilizadas? (s/N): n
⏭️  Imagens mantidas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Limpeza concluída!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Status atual:
...
```

## 🔗 Comandos úteis relacionados:

```bash
# Ver contêineres em execução
docker ps

# Ver todos os contêineres (incluindo parados)
docker ps -a

# Ver portas ocupadas
sudo lsof -i :PORTA

# Reiniciar Docker (último recurso)
sudo systemctl restart docker

# Parar e remover tudo de um docker-compose
docker compose down -v --remove-orphans
```

## 🆘 Problemas comuns:

### "Permission denied"
```bash
chmod +x cleanup-docker.sh
```

### "Cannot kill processes"
```bash
sudo ./cleanup-docker.sh
```

### Portas ainda ocupadas após limpeza
```bash
sudo systemctl restart docker
./cleanup-docker.sh
```

---

**Criado para resolver problemas de portas ocupadas no projeto AASTYPE2**
