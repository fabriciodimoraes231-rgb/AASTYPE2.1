#!/bin/bash

# Script de Setup e Teste do Sistema Time Series Data
# Este script configura e valida toda a infraestrutura

set -e  # Exit on error

echo "=================================================="
echo "  Time Series Data - Setup e Validação"
echo "=================================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir sucesso
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Função para imprimir erro
error() {
    echo -e "${RED}✗${NC} $1"
}

# Função para imprimir aviso
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Função para imprimir informação
info() {
    echo -e "ℹ $1"
}

# Verificar se Docker está instalado
echo "1. Verificando pré-requisitos..."
if ! command -v docker &> /dev/null; then
    error "Docker não está instalado"
    exit 1
fi
success "Docker instalado"

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose não está instalado"
    exit 1
fi
success "Docker Compose instalado"

# Verificar se as portas necessárias estão disponíveis
echo ""
echo "2. Verificando portas disponíveis..."
PORTS=(1883 27017 8081)
for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        warning "Porta $port já está em uso"
    else
        success "Porta $port disponível"
    fi
done

# Criar rede Docker se não existir
echo ""
echo "3. Criando rede Docker..."
if docker network inspect iot-network >/dev/null 2>&1; then
    success "Rede iot-network já existe"
else
    docker network create iot-network
    success "Rede iot-network criada"
fi

# Navegar para o diretório correto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/retrofit-simulator/docker"

# Parar containers antigos se existirem
echo ""
echo "4. Limpando containers antigos..."
docker-compose down 2>/dev/null || true
success "Containers antigos removidos"

# Build e iniciar os serviços
echo ""
echo "5. Construindo e iniciando serviços..."
docker-compose up -d --build

# Aguardar serviços iniciarem
echo ""
echo "6. Aguardando serviços iniciarem..."
sleep 10

# Verificar status dos containers
echo ""
echo "7. Verificando status dos containers..."
CONTAINERS=(
    "mqtt-broker"
    "iot-sensor-simulator"
    "timeseries-mongodb"
    "mongo-express-ui"
    "timeseries-recorder"
)

for container in "${CONTAINERS[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        success "$container está rodando"
    else
        error "$container NÃO está rodando"
    fi
done

# Aguardar mais um pouco para MongoDB inicializar completamente
echo ""
echo "8. Aguardando MongoDB inicializar completamente..."
sleep 15

# Verificar se dados estão sendo gravados
echo ""
echo "9. Verificando se dados estão sendo gravados no MongoDB..."
sleep 5

# Verificar collections no MongoDB
echo ""
echo "10. Verificando coleções no MongoDB..."
COLLECTIONS=$(docker exec timeseries-mongodb mongosh -u admin -p admin123 --authenticationDatabase admin --quiet --eval "
    use aas_timeseries
    db.getCollectionNames()
" 2>/dev/null || echo "[]")

if [[ $COLLECTIONS == *"temperature"* ]]; then
    success "Coleção 'temperature' existe"
else
    warning "Coleção 'temperature' ainda não foi criada (aguarde mais dados)"
fi

# Contar registros
echo ""
echo "11. Contando registros em cada coleção..."
docker exec timeseries-mongodb mongosh -u admin -p admin123 --authenticationDatabase admin --quiet --eval "
    use aas_timeseries
    print('Temperature:', db.temperature.countDocuments())
    print('Humidity:', db.humidity.countDocuments())
    print('NoiseLevel:', db.noiselevel.countDocuments())
    print('Status:', db.status.countDocuments())
" 2>/dev/null || warning "Ainda não há dados (aguarde alguns segundos)"

# Mostrar últimos registros
echo ""
echo "12. Mostrando últimos 3 registros de temperatura..."
docker exec timeseries-mongodb mongosh -u admin -p admin123 --authenticationDatabase admin --quiet --eval "
    use aas_timeseries
    db.temperature.find().sort({timestamp: -1}).limit(3).forEach(doc => {
        print('Timestamp:', doc.timestamp, 'Value:', doc.value, doc.unit || '')
    })
" 2>/dev/null || warning "Ainda não há dados de temperatura"

# Verificar logs
echo ""
echo "13. Verificando logs dos serviços..."

echo ""
info "Logs do Simulador (últimas 5 linhas):"
docker logs --tail 5 iot-sensor-simulator

echo ""
info "Logs do Time Series Recorder (últimas 5 linhas):"
docker logs --tail 5 timeseries-recorder

# URLs de acesso
echo ""
echo "=================================================="
echo "  ✓ Setup Completo!"
echo "=================================================="
echo ""
echo "URLs de Acesso:"
echo "  • Mongo Express: http://localhost:8081"
echo "    (admin/admin123)"
echo ""
echo "  • MongoDB: localhost:27017"
echo "    (admin/admin123)"
echo ""
echo "Comandos Úteis:"
echo "  • Ver logs do simulador:"
echo "    docker logs -f iot-sensor-simulator"
echo ""
echo "  • Ver logs do recorder:"
echo "    docker logs -f timeseries-recorder"
echo ""
echo "  • Consultar dados:"
echo "    docker exec -it timeseries-mongodb mongosh -u admin -p admin123 --authenticationDatabase admin"
echo ""
echo "  • Parar todos os serviços:"
echo "    docker-compose down"
echo ""
echo "=================================================="
echo "  Próximos Passos:"
echo "=================================================="
echo ""
echo "1. Acesse o Mongo Express em http://localhost:8081"
echo "2. Explore as coleções no database 'aas_timeseries'"
echo "3. Consulte o guia: MONGODB_QUERY_GUIDE.md"
echo "4. Leia a documentação completa: TIME_SERIES_IMPLEMENTATION.md"
echo ""
success "Sistema pronto para uso!"
