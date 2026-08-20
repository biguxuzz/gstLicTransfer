#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор buildcf/ для расширения GstLicTransfer.

Создаёт родительскую конфигурацию-заглушку для сборки расширения на CI:
  - buildcf/Catalogs/<Имя>.xml - МИНИМАЛЬНЫЕ заглушки каталогов:
    оригинальный UUID и имя объекта из БП 3.0.195.40, но без реквизитов,
    форм и макетов (ChildObjects пуст). Полные копии не подходят: они
    ссылаются на файлы форм/макетов и другие объекты БП, которых в buildcf
    нет, из-за чего платформа падает с "Файл объекта не существует".
    Для разрешения ссылок CatalogRef.<Имя> при импорте расширения
    достаточно самого факта существования каталога с тем же UUID.
  - buildcf/Languages/Русский.xml - копия из БП (XCF 2.21 -> 2.20)
  - buildcf/Configuration.xml  (родительская конфигурация-заглушка)
  - buildcf/ConfigDumpInfo.xml

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
    # ExchangePlan - заимствуется расширением (состав для сервиса 1С:МиграцияПриложений)
    ("ExchangePlan", "МиграцияПриложений", "b5c14196-5850-49a2-8f8a-1153f5f81e31"),
]

NS = ('xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" '
      'xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" '
      'xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" '
      'xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" '
      'xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" '
      'xmlns:pal="http://v8.1c.ru/8.1/data/ui/colors/palette" '
      'xmlns:style="http://v8.1c.ru/8.1/data/ui/style" '
      'xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" '
      'xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" '
      'xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" '
      'xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" '
      'xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" '
      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')


def read_acc(relpath):
    with open(os.path.join(ACC_ROOT, relpath), "rb") as f:
        raw = f.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8")


def write_file(relpath, text):
    dst = os.path.join(BUILDCF_ROOT, relpath)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as f:
        f.write(b"\xef\xbb\xbf")
        f.write(text.encode("utf-8"))


def generated_types(name):
    """Извлекает InternalInfo/GeneratedTypes оригинального каталога из БП."""
    src = read_acc(f"Catalogs/{name}.xml")
    m = re.search(r"<InternalInfo>.*?</InternalInfo>", src, re.S)
    return m.group(0) if m else "<InternalInfo/>"


def catalog_stub(name, synonym):
    """Минимальная заглушка каталога: uuid берется из PARENT_OBJECTS."""
    obj_uuid = dict((n, u) for _, n, u in PARENT_OBJECTS)[name]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS} version="2.20">
\t<Catalog uuid="{obj_uuid}">
\t\t{generated_types(name)}
\t\t<Properties>
\t\t\t<Name>{name}</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>{synonym}</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<Comment/>
\t\t\t<Hierarchical>false</Hierarchical>
\t\t\t<HierarchyType>HierarchyFoldersAndItems</HierarchyType>
\t\t\t<LimitLevelCount>false</LimitLevelCount>
\t\t\t<LevelCount>2</LevelCount>
\t\t\t<FoldersOnTop>true</FoldersOnTop>
\t\t\t<UseStandardCommands>true</UseStandardCommands>
\t\t\t<Owners/>
\t\t\t<SubordinationUse>ToItems</SubordinationUse>
\t\t\t<CodeLength>9</CodeLength>
\t\t\t<DescriptionLength>100</DescriptionLength>
\t\t\t<CodeType>String</CodeType>
\t\t\t<CodeAllowedLength>Variable</CodeAllowedLength>
\t\t\t<CodeSeries>WholeCatalog</CodeSeries>
\t\t\t<CheckUnique>false</CheckUnique>
\t\t\t<Autonumbering>false</Autonumbering>
\t\t\t<DefaultPresentation>AsDescription</DefaultPresentation>
\t\t\t<Characteristics/>
\t\t\t<QuickChoice>false</QuickChoice>
\t\t\t<ChoiceMode>BothWays</ChoiceMode>
\t\t\t<DefaultListForm/>
\t\t\t<DefaultChoiceForm/>
\t\t\t<DefaultObjectForm/>
\t\t\t<CreateOnInput>DontUse</CreateOnInput>
\t\t\t<ChoiceHistoryOnInput>DontUse</ChoiceHistoryOnInput>
\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>
\t\t\t<DataLockFields/>
\t\t\t<DataLockControlMode>Managed</DataLockControlMode>
\t\t\t<FullTextSearch>Use</FullTextSearch>
\t\t\t<ObjectPresentation/>
\t\t\t<ExtendedObjectPresentation/>
\t\t\t<ListPresentation/>
\t\t\t<ExtendedListPresentation/>
\t\t\t<Explanation/>
\t\t\t<HierarchyListPresentation/>
\t\t\t<ExtendedHierarchyListPresentation/>
\t\t\t<DataHistory>DontUse</DataHistory>
\t\t\t<UpdateDataHistoryImmediatelyAfterWrite>false</UpdateDataHistoryImmediatelyAfterWrite>
\t\t\t<ExecuteAfterWriteDataHistoryVersionProcessing>false</ExecuteAfterWriteDataHistoryVersionProcessing>
\t\t</Properties>
\t\t<ChildObjects/>
\t</Catalog>
</MetaDataObject>
"""


def main():
    print(f"Building {BUILDCF_ROOT}/ from {ACC_ROOT}")

    # 1. Заглушки каталогов
    synonyms = {"Организации": "Организации", "Контрагенты": "Контрагенты", "Пользователи": "Пользователи"}
    for obj_type, name, _ in PARENT_OBJECTS:
        if obj_type != "Catalog":
            continue
        write_file(f"Catalogs/{name}.xml", catalog_stub(name, synonyms[name]))
        print(f"  Wrote Catalogs/{name}.xml (stub)")

    # 2. Заглушка плана обмена МиграцияПриложений
    #    (мета из БП с вырезанными реквизитами/формами; Ext/Content.xml не нужен)
    plan = read_acc("ExchangePlans/МиграцияПриложений.xml")
    plan = plan.replace('version="2.21"', 'version="2.20"', 1)
    m = re.search(r"<ChildObjects>.*?</ChildObjects>", plan, re.S)
    assert m
    plan = plan.replace(m.group(0), "<ChildObjects/>")
    # вычистить ссылки на формы и команды, отсутствующие в заглушке
    plan = re.sub(r"(<Default(?:Object|List|Choice)Form>)[^<]+", lambda m: m.group(1), plan)
    plan = re.sub(r"(<DefaultRunForm>)[^<]+", lambda m: m.group(1), plan)
    write_file("ExchangePlans/МиграцияПриложений.xml", plan)
    print("  Wrote ExchangePlans/МиграцияПриложений.xml (stub)")

    # 2. Language Русский (копия из БП с понижением XCF-версии)
    lang = read_acc("Languages/Русский.xml")
    lang = lang.replace('version="2.21"', 'version="2.20"', 1)
    write_file("Languages/Русский.xml", lang)
    print("  Wrote Languages/Русский.xml")

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
<MetaDataObject {NS} version="2.20">
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
    write_file("Configuration.xml", cfg)
    print(f"  Wrote Configuration.xml ({len(PARENT_OBJECTS)+1} child objects)")


def write_config_dump_info():
    """Создаёт минимальный ConfigDumpInfo.xml."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<ConfigDumpInfo xmlns="http://v8.1c.ru/8.3/xcf/dumpinfo" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" format="Hierarchical" version="2.20">',
             '\t<ConfigVersions>']
    lines.append('\t\t<Metadata name="Configuration.Конфигурация" id="a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d" configVersion="a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1"/>')
    lines.append('\t\t<Metadata name="Language.Русский" id="db4a9ccb-9ef5-4b3c-8577-b6fe5db1b62e" configVersion="b1b1b1b1b1b1b1a1a1a1a1a1a1a1a1a1a1a1a1a1a1"/>')
    for obj_type, name, obj_uuid in PARENT_OBJECTS:
        lines.append('\t\t<Metadata name="%s.%s" id="%s" configVersion="%s"/>' % (
            obj_type, name, obj_uuid, obj_uuid[:40].replace("-", "")))
    lines.append('\t</ConfigVersions>')
    lines.append('</ConfigDumpInfo>')
    write_file("ConfigDumpInfo.xml", "\n".join(lines) + "\n")
    print(f"  Wrote ConfigDumpInfo.xml ({len(PARENT_OBJECTS)+2} records)")


if __name__ == "__main__":
    main()
