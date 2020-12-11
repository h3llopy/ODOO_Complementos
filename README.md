# ODOO_Complementos

Este repositorio contiene modulos complementarios referentes a la localizacion de `ODOO`.

- io_share_clientes_multicompany

**Descripción:**

- niq_pos_multi_barcodes       

**Descripción:** Módulo comprado y modificado. Contiene la funcionalidad de la lectura de multi codigos de barras en el punto de venta y en las pantallas asociadas a inventarios en el back. Ademas se realizó la modificación de la impresión de la etiqueta del producto para que incluya el código de barras.

- purchase_inventory_extend    

**Descripción:** Módulo desarrollado. Contiene la funcionalidad para que en la recepción del inventario de compras permita leer el codigo de barras para hacer más agil su ingreso

- pos_gift_card

**Descripción:** Módulo comprado y modificado. Permite el manejo de tarjetas Gift Card que serán redimidas en el consumo posterior del cliente que lo posea. Funciona con el POS

- pos_coupons                  

**Descripción:** Módulo comprado. Permite el manejo de cupones de descuento en la venta del POS

- wk_coupons                   

**Descripción:** Módulo comprado. Relacionado a la funcionalidad de pos_coupons

- pos_promotional_discounts

**Descripción:** Módulo comprado. Permite el manejo de promociones y descuentos en el POS. basados en filtro de clientes, productos, categorias y fechas.

- pos_partial_payment

**Descripción:** Módulo comprado. Permite la gestión de facturas de crédito en el POS.

- receive_purchase_barcode     

**Descripción:** Módulo desarrollado. Permite cargar un valor al producto en el POS en base a un porcentaje ingresado por el usuario. Aplica para cargo de Tarjetas de Credito en el POS.

- withholding_in_pos     

**Descripción:** Módulo que permite solicitar los datos de la retención en el POS

- pos_lot_credit_card, 

**Descripción:** Módulo que permite tomar los datos del lote y banco en el pos. 

- partner_type_identifier     

**Descripción:**
Asignación del tipo de identificador en el tercero indicando si es cedula es porque tiene 10 caracteres y si es ruc  es porque tiene 13 caracteres.

- odoo_multi_channel_sale y  shopify_odoo_bridge 

**Descripción:**
Inclusión de la importación del campo Company en shopify hacia el campo RUC/Cedula (VAT) en odoo.


  ## Dependencias entre modulos
  - pos_coupons y wk_coupons   
  - niq_pos_multi_barcodes y purchase_inventory_extend


## Autores ✒️

* **Nombre Desarrollador** - # Ticket - Descripcion Ticket

> **Note:** Agregarse aqui si modifica este modulo
