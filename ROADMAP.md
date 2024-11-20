# Roadmap

This document outlines planned improvements and potential future features for the JUDO Connectivity Module integration.

## Upcoming Changes

### High Priority

- [ ] Implement type safety for configuration files
  - Create TypedDict definitions for all YAML configurations
  - Add runtime validation
  - Add mypy type checking to CI pipeline

### Medium Priority

- [ ] Improve error handling
- [ ] Add more comprehensive logging
- [ ] Add configuration validation during startup

### Future Ideas

- [ ] Support for additional JUDO device types
- [ ] Automated testing with real device responses
- [ ] Configuration UI improvements

## Completed

- [x] Initial implementation of PROM-i-SAFE support
- [x] Basic entity configuration
- [x] API operation mapping

## Contributing

Have an idea? Please open a [feature request](https://github.com/christoefle/judo_connectivity_module/issues/new?template=feature_request.yml) to discuss it.

## Notes

### Type Safety Implementation Details

The plan is to:

1. Create strong types for all configuration files
2. Implement runtime validation
3. Add pre-commit hooks for validation
4. Document type system

Related files:

- `custom_components/judo_connectivity_module/api_spec/operations.yaml`
- `custom_components/judo_connectivity_module/api_spec/devices.yaml`
- `custom_components/judo_connectivity_module/config/entities.yaml`
- `custom_components/judo_connectivity_module/config/device_entities.yaml`
