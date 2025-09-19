# 🏗️ Arquitectura Modular - Guía de Desarrollo

**Patrón estándar de desarrollo para Caminando Online V4**

## 📋 Información General

**Fecha de creación**: Septiembre 2024
**Versión**: 1.0.0
**Estado**: Estándar de desarrollo activo
**Alcance**: Frontend - Componentes Angular

## 🎯 Propósito

Esta guía establece el patrón estándar de desarrollo modular para organizar el código de manera consistente, mantenible y escalable. Cada sección funcional debe tener su propia estructura modular independiente.

## 📂 Estructura Modular Estándar

### Arquitectura por Secciones

Cada sección del componente debe tener su propia estructura modular:

```
component/
├── component.html              # 📄 Template principal
├── styles/
│   ├── component.scss         # 🎨 Estilos generales
│   ├── section1.scss          # 🎯 Estilos específicos de section1
│   ├── section2.scss          # 🎯 Estilos específicos de section2
│   └── sectionN.scss          # 🎯 Estilos específicos de sectionN
└── scripts/
    ├── component.ts           # 🔧 Lógica principal del componente
    ├── section1.ts            # 🎯 Lógica específica de section1
    ├── section2.ts            # 🎯 Lógica específica de section2
    └── sectionN.ts            # 🎯 Lógica específica de sectionN
```

### Ejemplo Implementado

Basado en la implementación actual del componente `home`:

```
home/
├── home.html
├── styles/
│   ├── home.scss           # 🎨 Header, layout general
│   └── selectSupermarket.scss  # 🏪 Contenedor, botones, logos
└── scripts/
    ├── home.ts             # 🔧 Componente principal
    └── selectSupermarket.ts    # 🏪 Servicio, interface, utilidades
```

## 📝 Convenciones de Nomenclatura

### Archivos por Sección
- **`{component}.ts/scss`** → Componente principal (home.ts, home.scss)
- **`{section}.ts/scss`** → Módulos específicos de sección
- **`main.ts/scss`** → Utilidades generales (si aplica)

### Ejemplos de Nombres de Sección
- `selectSupermarket.ts/scss` → Selección de supermercados
- `categories.ts/scss` → Selección de categorías
- `products.ts/scss` → Lista y gestión de productos
- `cart.ts/scss` → Carrito de compras
- `checkout.ts/scss` → Proceso de pago
- `profile.ts/scss` → Perfil de usuario
- `orders.ts/scss` → Historial de pedidos
- `favorites.ts/scss` → Productos favoritos

### Reglas de Nomenclatura
- ✅ **Nombres descriptivos**: Deben describir exactamente la funcionalidad
- ✅ **Camel case**: `selectSupermarket`, `userProfile`, `productList`
- ✅ **Acciones claras**: `addToCart`, `removeFromCart`, `checkoutProcess`
- ✅ **Consistencia**: Mantener el mismo nombre en .ts y .scss

## 🔧 Estructura de Servicios por Sección

### Patrón de Servicio Estándar

Cada archivo `{section}.ts` debe seguir este patrón:

```typescript
// Interfaces específicas de la sección
export interface SectionData {
  id: string;
  name: string;
  // ... otros campos específicos
}

// Servicio principal de la sección
export class SectionService {
  private data: SectionData[] = [];
  private selectedItem: SectionData | null = null;

  // Constructor
  constructor() {
    this.initializeData();
  }

  // Inicialización de datos
  private initializeData(): void {
    // Lógica de inicialización
  }

  // Getters
  getData(): SectionData[] {
    return this.data;
  }

  getSelectedItem(): SectionData | null {
    return this.selectedItem;
  }

  // Métodos de selección
  selectItem(item: SectionData): SectionData {
    this.selectedItem = item;
    return item;
  }

  clearSelection(): void {
    this.selectedItem = null;
  }

  hasSelectedItem(): boolean {
    return this.selectedItem !== null;
  }

  // Métodos específicos de la sección
  // ... métodos personalizados según funcionalidad
}

// Utilidades de la sección
export class SectionUtils {
  static validateData(item: SectionData): boolean {
    // Validación específica
    return !!(item.id && item.name);
  }

  static formatData(item: SectionData): string {
    // Formateo específico
    return item.name;
  }

  static getDefaultItem(): SectionData {
    // Item por defecto
    return { id: '', name: '' };
  }
}
```

### Ejemplo Implementado - SelectSupermarket

```typescript
// Interfaces específicas de la sección
export interface Supermarket {
  id: string;
  name: string;
  logo: string;
}

// Servicio principal de la sección
export class SelectSupermarketService {
  private supermarkets: Supermarket[] = [
    { id: 'carrefour', name: 'Carrefour', logo: '🏪' },
    { id: 'jumbo', name: 'Jumbo', logo: '🛒' },
    { id: 'dia', name: 'Dia', logo: '🏬' },
    { id: 'vea', name: 'Vea', logo: '🛍️' },
    { id: 'disco', name: 'Disco', logo: '🏪' }
  ];

  private selectedSupermarket: Supermarket | null = null;

  getSupermarkets(): Supermarket[] {
    return this.supermarkets;
  }

  getSelectedSupermarket(): Supermarket | null {
    return this.selectedSupermarket;
  }

  selectSupermarket(supermarket: Supermarket): Supermarket {
    this.selectedSupermarket = supermarket;
    return supermarket;
  }

  clearSelection(): void {
    this.selectedSupermarket = null;
  }

  hasSelectedSupermarket(): boolean {
    return this.selectedSupermarket !== null;
  }
}
```

## 🎨 Estructura de Estilos por Sección

### Patrón de Estilos Estándar

Cada archivo `{section}.scss` debe contener:

```scss
// 🎯 Estilos específicos de la sección {section}

// Variables de la sección (opcional)
$section-primary-color: #4caf50;
$section-border-radius: 12px;

// Contenedor principal
.section-container {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: $section-border-radius;
  padding: 2rem;
  margin: 2rem 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid #dee2e6;
}

// Elementos específicos
.section-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 1rem;
  border: 2px solid $section-primary-color;
  background-color: white;
  color: $section-primary-color;
  border-radius: $section-border-radius;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: bold;
  transition: all 0.3s;
  text-align: center;
}

.section-item:hover {
  background-color: $section-primary-color;
  color: white;
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba($section-primary-color, 0.3);
}

// Sub-elementos específicos
.section-logo {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.section-name {
  font-size: 1rem;
}

.section-price {
  font-weight: bold;
  color: #ff9800;
}

// Estados específicos
.section-item.active {
  border-color: #ff9800;
  background-color: #fff3e0;
}

.section-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

// Responsive design
@media (max-width: 768px) {
  .section-container {
    padding: 1rem;
    margin: 1rem 0;
  }

  .section-item {
    padding: 1.5rem 0.75rem;
    font-size: 1rem;
  }
}
```

### Ejemplo Implementado - SelectSupermarket

```scss
// 🎯 Estilos específicos de la sección selectSupermarket

// Contenedor selectSupermarket
.selectSupermarket {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 16px;
  padding: 2rem;
  margin: 2rem 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid #dee2e6;

  .buttons-grid {
    margin-top: 1rem;
  }
}

// Botones de supermercados
.supermarket-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 1rem;
  border: 2px solid #4caf50;
  background-color: white;
  color: #4caf50;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: bold;
  transition: all 0.3s;
  text-align: center;
}

.supermarket-btn:hover {
  background-color: #4caf50;
  color: white;
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(76, 175, 80, 0.3);
}

.supermarket-logo {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.supermarket-name {
  font-size: 1rem;
}
```

## 🔗 Integración en Componente Principal

### Patrón de Integración Estándar

El componente principal debe importar y usar los servicios:

```typescript
import { Section1Service, Section1Data } from './scripts/section1';
import { Section2Service, Section2Data } from './scripts/section2';

@Component({
  selector: 'app-component',
  imports: [CommonModule],
  templateUrl: '../component.html',
  styleUrls: [
    '../styles/component.scss',
    '../styles/section1.scss',
    '../styles/section2.scss'
  ]
})
export class Component {
  // Servicios de secciones
  private section1Service = new Section1Service();
  private section2Service = new Section2Service();

  // Estados de navegación
  currentSection: 'section1' | 'section2' | 'section3' = 'section1';

  // Getters para acceso a datos
  get section1Data(): Section1Data[] {
    return this.section1Service.getData();
  }

  get selectedItem1(): Section1Data | null {
    return this.section1Service.getSelectedItem();
  }

  // Métodos delegados a servicios
  selectItem1(item: Section1Data) {
    this.section1Service.selectItem(item);
    this.navigateToNextSection();
  }

  selectItem2(item: Section2Data) {
    this.section2Service.selectItem(item);
    this.navigateToNextSection();
  }

  // Navegación entre secciones
  private navigateToNextSection(): void {
    // Lógica de navegación
  }

  // Métodos de navegación general
  goBack(): void {
    // Lógica de retroceso
  }
}
```

### Ejemplo Implementado - Home Component

```typescript
import { SelectSupermarketService, Supermarket } from './scripts/selectSupermarket';

@Component({
  selector: 'app-home',
  imports: [CommonModule],
  templateUrl: '../home.html',
  styleUrls: ['../styles/home.scss', '../styles/selectSupermarket.scss']
})
export class Home {
  // Servicio de sección
  private selectSupermarketService = new SelectSupermarketService();

  // Estados de las secciones
  currentSection: 'supermarket' | 'categories' | 'products' | 'cart' = 'supermarket';

  // Getters para acceso a datos
  get supermarkets(): Supermarket[] {
    return this.selectSupermarketService.getSupermarkets();
  }

  get selectedSupermarket(): Supermarket | null {
    return this.selectSupermarketService.getSelectedSupermarket();
  }

  // Métodos delegados
  selectSupermarket(supermarket: Supermarket) {
    this.selectSupermarketService.selectSupermarket(supermarket);
    this.currentSection = 'categories';
  }

  goBack() {
    if (this.currentSection === 'categories') {
      this.currentSection = 'supermarket';
      this.selectSupermarketService.clearSelection();
    }
    // ... más lógica
  }
}
```

## 🎯 Reglas de Identificación de Archivos

### Para Modificar Estilos
- **`component.scss`** → Cambios generales del componente (header, footer, layout)
- **`{section}.scss`** → Cambios específicos de esa sección (botones, contenedores)
- **`main.scss`** → Cambios de utilidades generales (variables, mixins)

### Para Modificar Lógica
- **`component.ts`** → Cambios en la integración general y navegación
- **`{section}.ts`** → Cambios en la lógica específica de esa sección
- **`main.ts`** → Cambios en utilidades generales y helpers

### Guía de Búsqueda
1. **¿Es un cambio general?** → `component.ts/scss`
2. **¿Es específico de una sección?** → `{section}.ts/scss`
3. **¿Es una utilidad compartida?** → `main.ts/scss`

## 📋 Checklist de Creación de Nueva Sección

### Antes de Crear
- [ ] **Nombre definido**: `{section}` describe exactamente la funcionalidad
- [ ] **Funcionalidad clara**: Requisitos específicos documentados
- [ ] **Dependencias identificadas**: Servicios o datos necesarios

### Durante la Creación
- [ ] **Archivos creados**: `{section}.ts` y `{section}.scss`
- [ ] **Servicio implementado**: `SectionService` con métodos estándar
- [ ] **Interface definida**: `SectionData` con campos específicos
- [ ] **Estilos organizados**: Contenedor principal y elementos específicos
- [ ] **Utilidades implementadas**: `SectionUtils` con validaciones y formateo

### Después de Crear
- [ ] **Integración completada**: Importado en componente principal
- [ ] **styleUrls actualizado**: Agregado al array de estilos
- [ ] **Navegación implementada**: Métodos de transición entre secciones
- [ ] **Compilación verificada**: Proyecto build sin errores
- [ ] **Documentación actualizada**: README con nueva sección

### Testing
- [ ] **Funcionalidad básica**: Selección y navegación funciona
- [ ] **Estados visuales**: Hover, active, disabled correctos
- [ ] **Responsive**: Diseño adaptativo en diferentes tamaños
- [ ] **Integración**: Comunicación correcta con otras secciones

## 🚀 Beneficios de Esta Arquitectura

### Desarrollo
- **🔍 Identificación rápida**: Nombres descriptivos facilitan encontrar archivos
- **🔧 Mantenimiento**: Cambios localizados en módulos específicos
- **👥 Colaboración**: Múltiples desarrolladores pueden trabajar en paralelo
- **📦 Reutilización**: Servicios pueden ser reutilizados en otros componentes

### Calidad
- **🧪 Testing**: Cada sección puede ser probada independientemente
- **🐛 Debugging**: Problemas aislados en módulos específicos
- **📊 Métricas**: Fácil medir cobertura de código por sección
- **🔒 Confiabilidad**: Cambios en una sección no afectan otras

### Escalabilidad
- **📈 Crecimiento**: Fácil agregar nuevas secciones siguiendo el patrón
- **🏗️ Arquitectura**: Estructura consistente en todo el proyecto
- **📚 Documentación**: Patrón claro y documentado
- **🔄 Evolución**: Fácil refactorizar siguiendo la misma estructura

## 🎯 Secciones Implementadas

### Completadas ✅
- [x] **selectSupermarket** - Selección de supermercados
  - `selectSupermarket.ts` - Servicio e interface
  - `selectSupermarket.scss` - Estilos del contenedor y botones

### Pendientes 📋
- [ ] **categories** - Selección de categorías de productos
- [ ] **products** - Lista y gestión de productos
- [ ] **cart** - Carrito de compras
- [ ] **checkout** - Proceso de pago
- [ ] **profile** - Perfil de usuario
- [ ] **orders** - Historial de pedidos

## 📚 Referencias

- **Ubicación**: `Sandbox/Experiments/frontend/src/public/app/home/`
- **Implementación actual**: Componente Home con selectSupermarket modular
- **Patrón base**: Arquitectura de servicios + estilos específicos
- **Convenciones**: Nombres descriptivos y estructura consistente

---

**Esta guía debe ser seguida para todo nuevo desarrollo en el proyecto.** 🎯

**Última actualización**: Septiembre 2024
**Versión**: 1.0.0
**Estado**: Estándar Activo ✅</content>
<parameter name="filePath">/Users/juanomac/Documents/dev/caminando-onlineV4/Sandbox/Experiments/frontend/src/public/app/home/ARQUITECTURA-MODULAR.md
