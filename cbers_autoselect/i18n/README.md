# Translation sources

The distributable plugin uses an automatically selected locale with source-English and Brazilian Portuguese strings in `../i18n.py`. This is fully functional without a separate runtime dependency.

For maintenance and future Qt Linguist integration, `cbers_autoselect_pt_BR.ts` exports these translations in Qt Linguist TS format. These TS strings can be reviewed in Qt Linguist. A compiled `.qm` will require a Qt `lrelease` tool, which is not bundled with this experimental prototype; unlike the locale dictionaries, the TS file is not loaded at runtime.
