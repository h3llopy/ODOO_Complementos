# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.1.1] - 2020-10-27

### Fixed
- Type check added for product.body_html.


## [1.1.0] - 2020-10-15

### Added
- Cursor based pagination
- Mark order paid on shopify
- Skip refunded orders on import

### Changed
- Dependency: ShopifyApi==8.0.0
- Customer addresses to be imported as invoice type to keep address field data
- Imported datetime string in order
- Address matching on order evaluation

### Fixed
- Export Product due lib update.
- Remove html tags from product description.

### Removed
- adjust_quantity in favour of set_quantity


## [1.0.8] - 2020-06-20

### Fixed
- Duplicate order.line.feed when import order again


## [1.0.7] - 2020-05-27

### Added
- Bulk Export from Instance fro now until odoo_multi_channel_sale 12.0 gets updated to handle it
