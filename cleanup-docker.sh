#!/bin/bash

# Script de limpeza Docker - Remove contêineres parados e processos zumbis
# Autor: GitHub Copilot
# Data: 15 de outubro de 2025

echo "🧹 Iniciando limpeza Docker..."
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Parar todos os contêineres em execução (opcional)
read -p "❓ Deseja parar todos os contêineres em execução? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}⏸️  Parando contêineres...${NC}"
    docker stop $(docker ps -q) 2>/dev/null
    echo -e "${GREEN}✅ Contêineres parados${NC}"
fi

# 2. Remover contêineres parados
echo -e "${YELLOW}🗑️  Removendo contêineres parados...${NC}"
STOPPED=$(docker ps -a -q -f status=exited -f status=created)
if [ -n "$STOPPED" ]; then
    docker rm $STOPPED
    echo -e "${GREEN}✅ Contêineres removidos${NC}"
else
    echo -e "${GREEN}✅ Nenhum contêiner parado encontrado${NC}"
fi

# 3. Verificar e matar processos docker-proxy zumbis nas portas específicas
PORTS=(1883 1884 9001 9002 8080 8081 4840 27017 27018 27019)
echo ""
echo -e "${YELLOW}🔍 Verificando processos docker-proxy nas portas...${NC}"

for PORT in "${PORTS[@]}"; do
    PIDS=$(sudo lsof -ti :$PORT 2>/dev/null | grep -v "^$")
    if [ -n "$PIDS" ]; then
        echo -e "${RED}⚠️  Porta $PORT ocupada pelos processos: $PIDS${NC}"
        read -p "   Deseja matar esses processos? (s/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            sudo kill -9 $PIDS 2>/dev/null
            echo -e "${GREEN}   ✅ Processos na porta $PORT eliminados${NC}"
        fi
    fi
done

# 4. Limpar redes não utilizadas
echo ""
echo -e "${YELLOW}🌐 Limpando redes não utilizadas...${NC}"
docker network prune -f
echo -e "${GREEN}✅ Redes limpas${NC}"

# 5. Limpar volumes órfãos (opcional - cuidado com dados!)
echo ""
read -p "❓ Deseja remover volumes não utilizados? ⚠️  ISSO REMOVE DADOS! (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${RED}🗑️  Removendo volumes não utilizados...${NC}"
    docker volume prune -f
    echo -e "${GREEN}✅ Volumes removidos${NC}"
else
    echo -e "${YELLOW}⏭️  Volumes mantidos${NC}"
fi

# 6. Limpar imagens não utilizadas (opcional)
echo ""
read -p "❓ Deseja remover imagens não utilizadas? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}🖼️  Removendo imagens não utilizadas...${NC}"
    docker image prune -f
    echo -e "${GREEN}✅ Imagens removidas${NC}"
else
    echo -e "${YELLOW}⏭️  Imagens mantidas${NC}"
fi

# 7. Mostrar status final
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Limpeza concluída!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📊 Status atual:"
echo ""
echo "🐳 Contêineres em execução:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "💾 Uso de disco Docker:"
docker system df
echo ""
echo -e "${GREEN}✨ Pronto para usar!${NC}"
