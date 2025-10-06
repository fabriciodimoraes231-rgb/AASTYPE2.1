# 🚀 Guia Passo-a-Passo Detalhado: AASX Package Explorer

## 📋 Pré-requisitos
- AASX Package Explorer instalado
- Arquivo `IoTSensors_Template.json` (disponível nesta pasta)
- Conhecimento básico de AAS

---

## 🎯 PARTE 1: IMPORTANDO O TEMPLATE

### 📥 **Passo 1.1: Abrir o Package Explorer**
1. **Inicie** o AASX Package Explorer
2. Você verá a tela inicial com uma árvore vazia à esquerda
3. **Menu superior**: File, Edit, View, Tools, Help

### 📥 **Passo 1.2: Importar Template Base**
1. **File → Open** (ou Ctrl+O)
2. **Navegue** até: `/home/manuel/AASTYPE2/iot-sensor-simulator/model/`
3. **Selecione**: `IoTSensors_Template.json`
4. **Clique**: "Open"

**✅ Resultado Esperado:**
```
📁 Environment
  📁 Submodels
    📄 IoTSensors
      📊 Temperature
      📊 Humidity  
      📊 NoiseLevel
      📁 OperationalStatus
        📊 Status
        📊 CpuUsage
        📊 MemoryUsage
        📊 UptimeHours
```

---

## 🔧 PARTE 2: CONFIGURANDO PROPRIEDADES

### 🌡️ **Passo 2.1: Configurar Temperature**
1. **Clique** em "Temperature" na árvore
2. **Painel direito** mostra as propriedades
3. **Configure:**

**Aba "Property":**
- **IdShort**: `Temperature` ✓
- **Value Type**: `xs:double` ✓
- **Value**: `25.0` ✓
- **Unit**: `°C` ✓

**Aba "Description":**
1. **Clique** no botão "+" para adicionar descrição
2. **Language**: `pt` | **Text**: `Temperatura ambiente medida pelo sensor`
3. **Clique** "+" novamente
4. **Language**: `en` | **Text**: `Ambient temperature measured by sensor`

**Aba "Semantic ID":**
1. **Type**: `ExternalReference`
2. **Keys** → **Add Key**:
   - **Type**: `GlobalReference`
   - **Value**: `0112/2///61360_7#AAA001#001`

### 💧 **Passo 2.2: Configurar Humidity**
1. **Clique** em "Humidity" na árvore
2. **Repita processo similar** ao Temperature:

**Property:**
- **Value**: `60.0`
- **Unit**: `%`

**Description:**
- **PT**: `Umidade relativa do ar medida pelo sensor`
- **EN**: `Relative air humidity measured by sensor`

**Semantic ID:**
- **Value**: `0112/2///61360_7#AAA002#001`

### 🔊 **Passo 2.3: Configurar NoiseLevel**
1. **Clique** em "NoiseLevel"
2. **Configure:**

**Property:**
- **Value**: `45.0`
- **Unit**: `dB`

**Description:**
- **PT**: `Nível de ruído medido pelo sensor`
- **EN**: `Noise level measured by sensor`

**Semantic ID:**
- **Value**: `0112/2///61360_7#AAA003#001`

---

## 📊 PARTE 3: CONFIGURANDO COLLECTION

### 📁 **Passo 3.1: OperationalStatus Collection**
1. **Clique** em "OperationalStatus"
2. **Verify Type**: `SubmodelElementCollection` ✓

**Description:**
- **PT**: `Informações sobre o status operacional do sistema`
- **EN**: `Information about the system operational status`

### 🔄 **Passo 3.2: Elementos da Collection**

**Para cada elemento (Status, CpuUsage, MemoryUsage, UptimeHours):**

1. **Clique** no elemento
2. **Configure valores:**

**Status:**
- **Type**: `xs:string`
- **Value**: `online`
- **Description (PT)**: `Status atual do sistema`

**CpuUsage:**
- **Type**: `xs:double`
- **Value**: `25.0`
- **Unit**: `%`
- **Description (PT)**: `Percentual de uso da CPU`

**MemoryUsage:**
- **Type**: `xs:double`
- **Value**: `45.0`
- **Unit**: `%`
- **Description (PT)**: `Percentual de uso da memória`

**UptimeHours:**
- **Type**: `xs:int`
- **Value**: `720`
- **Unit**: `h`
- **Description (PT)**: `Tempo de funcionamento contínuo`

---

## ⚡ PARTE 4: ADICIONANDO QUALIFIERS

### 🏷️ **Passo 4.1: Qualifiers para Dados Live**
Para **cada sensor** (Temperature, Humidity, NoiseLevel):

1. **Selecione** a propriedade
2. **Aba "Qualifiers"**
3. **Clique** "Add Qualifier"
4. **Configure:**
   - **Type**: `DataType`
   - **Value Type**: `xs:string`
   - **Value**: `Live`
   - **Semantic ID**:
     - **Type**: `ExternalReference`
     - **Value**: `https://carrier.com.br/qualifiers/DataType/1/0`

**💡 Dica:** Isso marca que os dados são atualizados em tempo real via MQTT!

---

## 🎨 PARTE 5: CUSTOMIZAÇÕES AVANÇADAS

### 📏 **Passo 5.1: Adicionar Constraints de Temperatura**
1. **Selecione** "Temperature"
2. **Qualifiers** → **Add Qualifier**
3. **Configure:**
   - **Type**: `ValueRange`
   - **Value**: `15,35`
   - **Description**: Faixa operacional do sensor

### 🔧 **Passo 5.2: Configurar Submodel Principal**
1. **Clique** em "IoTSensors" (raiz do submodel)
2. **Aba "Submodel"**:
   - **Kind**: `Instance` (não Template!)
   - **ID**: `https://carrier.com.br/ids/sm/IoTSensors/1/0`

**Administration:**
- **Version**: `1`
- **Revision**: `0`

---

## 💾 PARTE 6: SALVANDO E EXPORTANDO

### 💾 **Passo 6.1: Salvar Trabalho**
1. **File → Save** (Ctrl+S)
2. **Nome**: `IoTSensors_WorkInProgress.json`

### � **Passo 6.2: Exportar Final**
1. **File → Save As**
2. **Formato options:**
   - **JSON**: Para usar com FAAAST Service
   - **AASX**: Para compartilhar/distribuir
   - **XML**: Para outros sistemas

**Recomendado**: Exporte ambos JSON e AASX

---

## 🔗 PARTE 7: INTEGRAÇÃO COM AAS PRINCIPAL

### 🔄 **Passo 7.1: Adicionar ao AAS Ar Condicionado**
1. **File → Open**: `ArCondicionadoAAS.json`
2. **Na árvore**, expanda o AAS principal
3. **Clique direito** em "Submodels"
4. **Add Reference**:
   - **Type**: `ModelReference`
   - **Key Type**: `Submodel`
   - **Value**: `https://carrier.com.br/ids/sm/IoTSensors/1/0`

### 📋 **Passo 7.2: Copiar Submodel**
**Método Copy/Paste:**
1. **Abra** `IoTSensors_Template.json` em nova janela
2. **Clique direito** no submodel "IoTSensors"
3. **Copy**
4. **Volte** para `ArCondicionadoAAS.json`
5. **Clique direito** em "Submodels"
6. **Paste**

---

## ✅ PARTE 8: VALIDAÇÃO E TESTE

### 🔍 **Passo 8.1: Verificar Estrutura**
**Checklist final:**
- [ ] Submodel ID único e correto
- [ ] Todas as propriedades com tipos corretos
- [ ] Descrições em PT e EN
- [ ] Semantic IDs configurados
- [ ] Qualifiers "Live" adicionados
- [ ] Unidades corretas
- [ ] Collection OperationalStatus completa

### 📊 **Passo 8.2: Preview dos Dados**
1. **View → Preview**
2. Verifique como ficará a visualização
3. **Tools → Validate** para verificar erros

### 🚀 **Passo 8.3: Preparar para FAAAST**
1. **Export** como JSON final
2. **Copie** para pasta do FAAAST Service
3. **Próximo**: Configurar MQTT connections

---

## 🎯 DICAS E ATALHOS

### ⌨️ **Atalhos Úteis**
- **Ctrl+N**: Novo elemento
- **Ctrl+D**: Duplicar elemento selecionado
- **F2**: Renomear elemento
- **Del**: Deletar elemento
- **Ctrl+S**: Salvar
- **Ctrl+Z**: Desfazer
- **Ctrl+Y**: Refazer

### 💡 **Dicas Pro**
1. **Use Templates**: Sempre comece com template base
2. **Batch Operations**: Selecione múltiplos elementos para edição em lote
3. **Validation**: Use Tools → Validate regularmente
4. **Backup**: Salve versões intermediárias
5. **Semantic IDs**: Use biblioteca padrão quando possível

### � **Troubleshooting**
**Problema**: "Semantic ID not found"
**Solução**: Use GlobalReference com IDs completos

**Problema**: "Invalid value type"
**Solução**: Verifique se valor corresponde ao tipo (ex: número para xs:double)

**Problema**: "Missing descriptions"
**Solução**: Adicione pelo menos uma descrição em inglês

---

## � **Próximos Passos**
Após completar este guia:
1. ✅ Submodel criado no Package Explorer
2. 🔧 [Configurar FAAAST Service](../config/)
3. 🐳 [Rodar Docker environment](../docker/)
4. 📡 [Testar conexão MQTT](../test/)

**Tempo estimado**: 30-45 minutos para usuário iniciante