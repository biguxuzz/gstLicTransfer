#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор buildcf/ для расширения GstLicTransfer.

Берёт оригинальные файлы из E:\\temp\\acc\\ (выгрузка 1С:Бухгалтерии
предприятия 3.0.195.40) для каждого объекта, типы которого используются
расширением, и кладёт их в buildcf/<Type>/<Name>.xml с понижением XCF
version 2.21 -> 2.20 (требование платформы 8.3.27 на CI). Также создаёт:
  - buildcf/Languages/Русский.xml
  - buildcf/Configuration.xml  (родительская конфигурация-заглушка)
  - buildcf/ConfigDumpInfo.xml

Расширение НЕ заимствует объекты основной конфигурации (нет adopted-объектов,
кроме языка), но реквизиты новых объектов ссылаются на типы
СправочникСсылка.Организации/Контрагенты/Пользователи, поэтому эти каталоги
должны присутствовать в родительской конфигурации при сборке .cfe на CI.

Запуск:
  cd E:\\git\\gstLicTransfer
  python buildcf\\_generate.py
"""

import os
import re

# === Настройки ===
ACC_ROOT = r"E:\temp\acc"
BUILDCF_ROOT = "buildcf"

# Таблица: (Тип, Имя, UUID объекта в основной конфигурации)
# Источник: выгрузка E:\temp\acc (БП 3.0.195.40)
PARENT_OBJECTS = [
    # Catalogs - типы реквизитов документа ПередачаЛицензий
    ("Catalog", "Организации",   "fd0c3124-91f5-4c1e-bbc0-f2163e61ff2a"),
    ("Catalog", "Контрагенты",   "51b9a2d4-bd53-4f40-824e-e3b4e323279e"),
    ("Catalog", "Пользователи",  "bffeceba-fe82-4593-9d34-edc03d99fa44"),
]

# Каталоги во множественном числе (XCF convention)
TYPE_DIRS = {
    "Catalog": "Catalogs",
    "Language": "Languages",
}


def downgrade_xcf(content):
    """Понижает version='2.21' -> '2.20' в MetaDataObject."""
    return content.replace('version="2.21"', 'version="2.20"', 1)


def copy_with_downgrade(src, dst):
    """Копирует файл из src в dst, сохраняя BOM и понижая XCF version."""
    with open(src, "rb") as f:
        raw = f.read()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    if has_bom:
        raw = raw[3:]
    text = raw.decode("utf-8")
    text = downgrade_xcf(text)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as f:
        if has_bom:
            f.write(b"\xef\xbb\xbf")
        f.write(text.encode("utf-8"))


def main():
    print(f"Building {BUILDCF_ROOT}/ from {ACC_ROOT}")

    # 1. Копируем каждый объект родительской конфигурации
    copied = 0
    missing = []
    for obj_type, name, obj_uuid in PARENT_OBJECTS:
        type_dir = TYPE_DIRS[obj_type]
        src = os.path.join(ACC_ROOT, type_dir, f"{name}.xml")
        dst = os.path.join(BUILDCF_ROOT, type_dir, f"{name}.xml")
        if not os.path.exists(src):
            missing.append(src)
            continue
        copy_with_downgrade(src, dst)
        copied += 1
    print(f"  Copied {copied} parent objects")
    if missing:
        print(f"  MISSING {len(missing)} files:")
        for m in missing:
            print(f"    {m}")

    # 2. Language Русский
    src_lang = os.path.join(ACC_ROOT, "Languages", "Русский.xml")
    dst_lang = os.path.join(BUILDCF_ROOT, "Languages", "Русский.xml")
    copy_with_downgrade(src_lang, dst_lang)
    print(f"  Copied Language.Русский")

    # 3. Configuration.xml (родительская конфигурация)
    write_configuration()

    # 4. ConfigDumpInfo.xml
    write_config_dump_info()

    print(f"\nDone. {BUILDCF_ROOT}/ ready.")


def write_configuration():
    """Создаёт минимальный Configuration.xml для родительской конфигурации."""
    child_lines = ['\t\t<Language>Русский</Language>']
    for obj_type, name, _ in PARENT_OBJECTS:
        child_lines.append(f'\t\t<{obj_type}>{name}</{obj_type}>')
    child_objects = "\n".join(child_lines)

    cfg = f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:pal="http://v8.1c.ru/8.1/data/ui/colors/palette" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<Configuration uuid="a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d">
\t\t<InternalInfo>
\t\t\t<xr:ContainedObject>
\t\t\t\t<xr:ClassId>9cd510cd-abfc-11d4-9434-004095e12fc7</xr:ClassId>
\t\t\t\t<xr:ObjectId>1a2b3c4d-5e6f-402a-b345-67890abcdef0</xr:ObjectId>
\t\t\t</xr:ContainedObject>
\t\t\t<xr:ContainedObject>
\t\t\t\t<xr:ClassId>9fcd25a0-4822-11d4-9414-008048da11f9</xr:ClassId>
\t\t\t\t<xr:ObjectId>2b3c4d5e-6f70-413b-c456-78901abcdef1</xr:ObjectId>
\t\t\t</xr:ContainedObject>
\t\t\t<xr:ContainedObject>
\t\t\t\t<xr:ClassId>e3687481-0a87-462c-a166-9f34594f9bba</xr:ClassId>
\t\t\t\t<xr:ObjectId>3c4d5e6f-7081-424c-d567-89012abcdef2</xr:ObjectId>
\t\t\t</xr:ContainedObject>
\t\t\t<xr:ContainedObject>
\t\t\t\t<xr:ClassId>9de14907-ec23-4a07-96f0-85521cb6b53b</xr:ClassId>
\t\t\t\t<xr:ObjectId>4d5e6f70-8192-435d-e678-90123abcdef3</xr:ObjectId>
\t\t\t</xr:ContainedObject>
\t\t\t<xr:ContainedObject>
\t\t\t\t<xr:ClassId>51f2d5d8-ea4d-4064-8892-82951750031e</xr:ClassId>
\t\t\t\t<xr:ObjectId>5e6f7081-92a3-446e-f789-01234abcdef4</xr:ObjectId>
\t\t\t</xr:ContainedObject>
\t\t\t<xr:ContainedObject>
\t\t\t\t<xr:ClassId>e68182ea-4237-4383-967f-90c1e3370bc7</xr:ClassId>
\t\t\t\t<xr:ObjectId>6f708192-a3b4-457f-0890-12345abcdef5</xr:ObjectId>
\t\t\t</xr:ContainedObject>
\t\t\t<xr:ContainedObject>
\t\t\t\t<xr:ClassId>fb282519-d103-4dd3-bc12-cb271d631dfc</xr:ClassId>
\t\t\t\t<xr:ObjectId>708192a3-b4c5-4680-1901-23456abcdef6</xr:ObjectId>
\t\t\t</xr:ContainedObject>
\t\t</InternalInfo>
\t\t<Properties>
\t\t\t<Name>Конфигурация</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Конфигурация</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<Comment/>
\t\t\t<NamePrefix/>
\t\t\t<ConfigurationExtensionCompatibilityMode>Version8_3_27</ConfigurationExtensionCompatibilityMode>
\t\t\t<DefaultRunMode>ManagedApplication</DefaultRunMode>
\t\t\t<UsePurposes>
\t\t\t\t<v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>
\t\t\t</UsePurposes>
\t\t\t<ScriptVariant>Russian</ScriptVariant>
\t\t\t<DefaultRoles/>
\t\t\t<Vendor/>
\t\t\t<Version/>
\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>
\t\t\t<UseManagedFormInOrdinaryApplication>false</UseManagedFormInOrdinaryApplication>
\t\t\t<UseOrdinaryFormInManagedApplication>false</UseOrdinaryFormInManagedApplication>
\t\t\t<DefaultLanguage>Language.Русский</DefaultLanguage>
\t\t\t<BriefInformation/>
\t\t\t<DetailedInformation/>
\t\t\t<Copyright/>
\t\t\t<VendorInformationAddress/>
\t\t\t<ConfigurationInformationAddress/>
\t\t\t<DataLockControlMode>Managed</DataLockControlMode>
\t\t\t<ModalityUseMode>DontUse</ModalityUseMode>
\t\t\t<SynchronousPlatformExtensionAndAddInCallUseMode>DontUse</SynchronousPlatformExtensionAndAddInCallUseMode>
\t\t\t<InterfaceCompatibilityMode>TaxiEnableVersion8_2</InterfaceCompatibilityMode>
\t\t\t<CompatibilityMode>Version8_3_27</CompatibilityMode>
\t\t\t<DefaultConstantsForm/>
\t\t</Properties>
\t\t<ChildObjects>
{child_objects}
\t\t</ChildObjects>
\t</Configuration>
</MetaDataObject>
"""
    dst = os.path.join(BUILDCF_ROOT, "Configuration.xml")
    with open(dst, "wb") as f:
        f.write(b"\xef\xbb\xbf")
        f.write(cfg.encode("utf-8"))
    print(f"  Wrote Configuration.xml ({len(PARENT_OBJECTS)+1} child objects)")


def write_config_dump_info():
    """Создаёт минимальный ConfigDumpInfo.xml."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<ConfigDumpInfo xmlns="http://v8.1c.ru/8.3/xcf/dumpinfo" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" format="Hierarchical" version="2.20">',
             '\t<ConfigVersions>']
    # Configuration
    lines.append('\t\t<Metadata name="Configuration.Конфигурация" id="a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d" configVersion="a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1"/>')
    # Language
    lines.append('\t\t<Metadata name="Language.Русский" id="db4a9ccb-9ef5-4b3c-8577-b6fe5db1b62e" configVersion="b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1"/>')
    # Родительские объекты
    for obj_type, name, obj_uuid in PARENT_OBJECTS:
        lines.append('\t\t<Metadata name="%s.%s" id="%s" configVersion="%s"/>' % (
            obj_type, name, obj_uuid, obj_uuid[:40].replace("-", "")))
    lines.append('\t</ConfigVersions>')
    lines.append('</ConfigDumpInfo>')
    dst = os.path.join(BUILDCF_ROOT, "ConfigDumpInfo.xml")
    with open(dst, "wb") as f:
        f.write(b"\xef\xbb\xbf")
        f.write(("\n".join(lines) + "\n").encode("utf-8"))
    print(f"  Wrote ConfigDumpInfo.xml ({len(PARENT_OBJECTS)+2} records)")


if __name__ == "__main__":
    main()
