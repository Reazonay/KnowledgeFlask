Das ist ein fantastischer Plan und eine detaillierte Spezifikation! Da kein Startcode zur Verfügung gestellt wurde, werde ich das komplette System basierend auf deinen Anforderungen und den beschriebenen Verbesserungen von Grund auf neu implementieren. Das resultierende Programm wird ein robustes, CLI-basiertes Tool zur Verwaltung von KI-Agenten, deren Wissensbasen und Versionen sein, inklusive des gewünschten Error-Handlings und der simulierten Persistenz.

Ich habe mich für eine `knowledge.json`-Datei entschieden, die eine Liste von String-Dokumenten enthält. Dies bietet die Struktur von JSON und erfüllt gleichzeitig die Anforderung der "zeilenweisen" Speicherung von Dokumenten.

---

Hier ist der KOMPLETTE neue Code für 'KnowledgeFlask':


import argparse
import datetime
import json
import os
import shutil
import sys
import uuid # Für eindeutige Versions-IDs

# --- 0. Konfiguration und Konstanten ---
# Basisverzeichnis für KnowledgeFlask-Daten
# Standardmäßig im Benutzer-Home-Verzeichnis unter .knowledge_flask
# Kann auch manuell gesetzt werden, z.B. os.path.join(os.getcwd(), "knowledge_flask_data")
KNOWLEDGE_FLASK_BASE_DIR = os.path.join(os.path.expanduser("~"), ".knowledge_flask")

AGENTS_DIR_NAME = "agents"
KNOWLEDGE_FILE_NAME = "knowledge.json"
VERSIONS_DIR_NAME = "versions"
VERSION_METADATA_FILE_NAME = "version_meta.json"

# --- 1. Custom Exceptions ---
class KnowledgeFlaskException(Exception):
    """Basis-Exception für KnowledgeFlask-Fehler."""
    pass

class AgentNotFoundError(KnowledgeFlaskException):
    """Wird ausgelöst, wenn ein angeforderter Agent nicht gefunden wird."""
    def __init__(self, agent_name):
        super().__init__(f"Agent '{agent_name}' wurde nicht gefunden.")
        self.agent_name = agent_name

class AgentAlreadyExistsError(KnowledgeFlaskException):
    """Wird ausgelöst, wenn versucht wird, einen Agenten zu erstellen, der bereits existiert."""
    def __init__(self, agent_name):
        super().__init__(f"Agent '{agent_name}' existiert bereits.")
        self.agent_name = agent_name

class VersionNotFoundError(KnowledgeFlaskException):
    """Wird ausgelöst, wenn eine angeforderte Version nicht gefunden wird."""
    def __init__(self, version_id, agent_name=None):
        msg = f"Version '{version_id}' wurde nicht gefunden."
        if agent_name:
            msg += f" für Agent '{agent_name}'."
        super().__init__(msg)
        self.version_id = version_id
        self.agent_name = agent_name

# --- 2. Manager-Klassen ---

class KnowledgeBaseManager:
    """
    Verwaltet die Wissensbasis eines einzelnen Agenten.
    Simuliert Persistenz durch Speicherung in einer JSON-Datei.
    """
    def __init__(self, agent_path: str):
        self.agent_path = agent_path
        self.knowledge_file_path = os.path.join(agent_path, KNOWLEDGE_FILE_NAME)
        # Stelle sicher, dass das Agentenverzeichnis existiert
        os.makedirs(self.agent_path, exist_ok=True)

    def _load_knowledge_from_file(self) -> list[str]:
        """Lädt die Wissensbasis aus der JSON-Datei."""
        if not os.path.exists(self.knowledge_file_path):
            return []
        try:
            with open(self.knowledge_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    print(f"Warnung: Wissensdatei '{self.knowledge_file_path}' enthält kein gültiges JSON-Array. Wird geleert.", file=sys.stderr)
                    return []
                return [str(item) for item in data] # Stellen Sie sicher, dass alles Strings sind
        except json.JSONDecodeError as e:
            print(f"Fehler beim Decodieren der Wissensdatei '{self.knowledge_file_path}': {e}. Datei wird ignoriert.", file=sys.stderr)
            return []
        except IOError as e:
            raise KnowledgeFlaskException(f"Fehler beim Lesen der Wissensdatei '{self.knowledge_file_path}': {e}") from e

    def _save_knowledge_to_file(self, knowledge_data: list[str]):
        """Speichert die Wissensbasis in die JSON-Datei."""
        try:
            with open(self.knowledge_file_path, 'w', encoding='utf-8') as f:
                json.dump(knowledge_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise KnowledgeFlaskException(f"Fehler beim Schreiben der Wissensdatei '{self.knowledge_file_path}': {e}") from e

    def add_knowledge(self, knowledge_item: str):
        """Fügt ein Wissenselement hinzu, prüft auf Duplikate."""
        knowledge = self._load_knowledge_from_file()
        if knowledge_item not in knowledge:
            knowledge.append(knowledge_item)
            self._save_knowledge_to_file(knowledge)
            print(f"Wissen hinzugefügt: '{knowledge_item[:50]}...'")
        else:
            print(f"Wissen '{knowledge_item[:50]}...' ist bereits vorhanden.")

    def get_knowledge(self) -> list[str]:
        """Gibt die gesamte Wissensbasis zurück."""
        return self._load_knowledge_from_file()

    def delete_knowledge_base_file(self):
        """Löscht die Wissensbasis-Datei."""
        if os.path.exists(self.knowledge_file_path):
            try:
                os.remove(self.knowledge_file_path)
                print(f"Wissensdatei '{KNOWLEDGE_FILE_NAME}' gelöscht.")
            except OSError as e:
                raise KnowledgeFlaskException(f"Fehler beim Löschen der Wissensdatei '{self.knowledge_file_path}': {e}") from e

class VersionManager:
    """
    Verwaltet Versionen der Wissensbasis eines Agenten.
    Jede Version ist ein Snapshot der knowledge.json.
    """
    def __init__(self, agent_path: str):
        self.agent_path = agent_path
        self.versions_dir = os.path.join(agent_path, VERSIONS_DIR_NAME)
        self.knowledge_file_path = os.path.join(agent_path, KNOWLEDGE_FILE_NAME)
        os.makedirs(self.versions_dir, exist_ok=True)

    def _get_version_path(self, version_id: str) -> str:
        """Gibt den vollständigen Pfad zu einem Versionsverzeichnis zurück."""
        return os.path.join(self.versions_dir, version_id)

    def _get_version_metadata_file_path(self, version_path: str) -> str:
        """Gibt den Pfad zur Metadaten-Datei einer Version zurück."""
        return os.path.join(version_path, VERSION_METADATA_FILE_NAME)

    def _load_version_metadata(self, version_path: str) -> dict:
        """Lädt Metadaten für eine bestimmte Version."""
        metadata_file = self._get_version_metadata_file_path(version_path)
        if not os.path.exists(metadata_file):
            return {} # Keine Metadaten vorhanden
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Fehler beim Decodieren der Metadaten '{metadata_file}': {e}. Leere Metadaten werden zurückgegeben.", file=sys.stderr)
            return {}
        except IOError as e:
            raise KnowledgeFlaskException(f"Fehler beim Lesen der Metadaten '{metadata_file}': {e}") from e

    def _save_version_metadata(self, version_path: str, metadata: dict):
        """Speichert Metadaten für eine bestimmte Version."""
        metadata_file = self._get_version_metadata_file_path(version_path)
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise KnowledgeFlaskException(f"Fehler beim Schreiben der Metadaten '{metadata_file}': {e}") from e

    def create_version(self, description: str = None) -> str:
        """
        Erstellt eine neue Version der Wissensbasis.
        Kopiert die aktuelle knowledge.json und speichert Metadaten.
        """
        if not os.path.exists(self.knowledge_file_path):
            raise KnowledgeFlaskException("Keine Wissensbasis vorhanden, um eine Version zu erstellen.")

        version_id = str(uuid.uuid4()) # Eindeutige ID für die Version
        version_path = self._get_version_path(version_id)
        os.makedirs(version_path, exist_ok=True)

        try:
            shutil.copyfile(self.knowledge_file_path, os.path.join(version_path, KNOWLEDGE_FILE_NAME))
        except shutil.Error as e:
            raise KnowledgeFlaskException(f"Fehler beim Kopieren der Wissensdatei für Version '{version_id}': {e}") from e

        metadata = {
            "id": version_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "description": description if description else "Keine Beschreibung"
        }
        self._save_version_metadata(version_path, metadata)
        return version_id

    def restore_version(self, version_id: str):
        """
        Stellt eine frühere Version der Wissensbasis wieder her.
        Überschreibt die aktuelle knowledge.json.
        """
        version_path = self._get_version_path(version_id)
        if not os.path.exists(version_path):
            raise VersionNotFoundError(version_id)

        version_knowledge_file = os.path.join(version_path, KNOWLEDGE_FILE_NAME)
        if not os.path.exists(version_knowledge_file):
            raise KnowledgeFlaskException(f"Wissensdatei für Version '{version_id}' nicht gefunden. Version ist möglicherweise korrupt.")

        try:
            shutil.copyfile(version_knowledge_file, self.knowledge_file_path)
            print(f"Wissensbasis von Version '{version_id}' erfolgreich wiederhergestellt.")
        except shutil.Error as e:
            raise KnowledgeFlaskException(f"Fehler beim Wiederherstellen der Version '{version_id}': {e}") from e

    def list_versions(self) -> list[dict]:
        """Listet alle verfügbaren Versionen mit Metadaten auf."""
        versions = []
        if not os.path.exists(self.versions_dir):
            return versions

        for version_id in os.listdir(self.versions_dir):
            version_path = self._get_version_path(version_id)
            if os.path.isdir(version_path):
                metadata = self._load_version_metadata(version_path)
                if metadata: # Stelle sicher, dass Metadaten geladen wurden
                    versions.append(metadata)
                else:
                    versions.append({"id": version_id, "timestamp": "Unbekannt", "description": "Metadaten fehlen/fehlerhaft"})
        
        # Sortiere nach Zeitstempel absteigend
        versions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return versions

    def delete_version(self, version_id: str):
        """Löscht eine bestimmte Version."""
        version_path = self._get_version_path(version_id)
        if not os.path.exists(version_path):
            raise VersionNotFoundError(version_id)

        try:
            shutil.rmtree(version_path)
            print(f"Version '{version_id}' erfolgreich gelöscht.")
        except OSError as e:
            raise KnowledgeFlaskException(f"Fehler beim Löschen der Version '{version_id}': {e}") from e

# --- 3. Hauptanwendungsklasse ---

class KnowledgeFlask:
    """
    Die zentrale Anwendungsklasse zur Verwaltung von Agenten,
    deren Wissensbasen und Versionen.
    """
    def __init__(self, base_dir: str = KNOWLEDGE_FLASK_BASE_DIR):
        self.base_dir = os.path.abspath(base_dir)
        self.agents_dir = os.path.join(self.base_dir, AGENTS_DIR_NAME)
        
        try:
            os.makedirs(self.agents_dir, exist_ok=True)
        except OSError as e:
            raise KnowledgeFlaskException(f"Fehler beim Initialisieren des Basisverzeichnisses '{self.agents_dir}': {e}") from e

    def _get_agent_path(self, agent_name: str) -> str:
        """Gibt den vollständigen Pfad zu einem Agentenverzeichnis zurück."""
        return os.path.join(self.agents_dir, agent_name)

    def _agent_exists(self, agent_name: str) -> bool:
        """Prüft, ob ein Agentenverzeichnis existiert."""
        return os.path.isdir(self._get_agent_path(agent_name))

    def create_agent(self, agent_name: str):
        """Erstellt einen neuen Agenten."""
        agent_path = self._get_agent_path(agent_name)
        if self._agent_exists(agent_name):
            raise AgentAlreadyExistsError(agent_name)
        
        try:
            os.makedirs(agent_path)
            # Initialisiere die KnowledgeBase für den neuen Agenten
            KnowledgeBaseManager(agent_path)._save_knowledge_to_file([]) 
            VersionManager(agent_path) # Stellen Sie sicher, dass der Versionsordner initialisiert wird
            print(f"Agent '{agent_name}' erfolgreich erstellt in '{agent_path}'.")
        except OSError as e:
            raise KnowledgeFlaskException(f"Fehler beim Erstellen des Agenten '{agent_name}': {e}") from e

    def delete_agent(self, agent_name: str):
        """Löscht einen bestehenden Agenten und all seine Daten."""
        agent_path = self._get_agent_path(agent_name)
        if not self._agent_exists(agent_name):
            raise AgentNotFoundError(agent_name)
        
        try:
            shutil.rmtree(agent_path)
            print(f"Agent '{agent_name}' und alle zugehörigen Daten wurden erfolgreich gelöscht.")
        except OSError as e:
            raise KnowledgeFlaskException(f"Fehler beim Löschen des Agenten '{agent_name}': {e}") from e
        except shutil.Error as e:
            raise KnowledgeFlaskException(f"Fehler beim Löschen des Agentenverzeichnisses '{agent_name}': {e}") from e

    def list_agents(self) -> list[str]:
        """Listet alle vorhandenen Agenten auf."""
        if not os.path.exists(self.agents_dir):
            return []
        agents = [d for d in os.listdir(self.agents_dir) if os.path.isdir(self._get_agent_path(d))]
        return sorted(agents)

    def add_knowledge(self, agent_name: str, knowledge_item: str):
        """Fügt einem Agenten Wissen hinzu."""
        agent_path = self._get_agent_path(agent_name)
        if not self._agent_exists(agent_name):
            raise AgentNotFoundError(agent_name)
        
        kb_manager = KnowledgeBaseManager(agent_path)
        kb_manager.add_knowledge(knowledge_item)

    def get_knowledge(self, agent_name: str) -> list[str]:
        """Ruft die Wissensbasis eines Agenten ab."""
        agent_path = self._get_agent_path(agent_name)
        if not self._agent_exists(agent_name):
            raise AgentNotFoundError(agent_name)
        
        kb_manager = KnowledgeBaseManager(agent_path)
        return kb_manager.get_knowledge()

    def create_version(self, agent_name: str, description: str = None) -> str:
        """Erstellt eine Version der Wissensbasis eines Agenten."""
        agent_path = self._get_agent_path(agent_name)
        if not self._agent_exists(agent_name):
            raise AgentNotFoundError(agent_name)
        
        version_manager = VersionManager(agent_path)
        version_id = version_manager.create_version(description)
        print(f"Version '{version_id}' für Agent '{agent_name}' erfolgreich erstellt.")
        return version_id

    def restore_version(self, agent_name: str, version_id: str):
        """Stellt eine Version der Wissensbasis eines Agenten wieder her."""
        agent_path = self._get_agent_path(agent_name)
        if not self._agent_exists(agent_name):
            raise AgentNotFoundError(agent_name)
        
        version_manager = VersionManager(agent_path)
        version_manager.restore_version(version_id)
        print(f"Version '{version_id}' für Agent '{agent_name}' erfolgreich wiederhergestellt.")

    def list_versions(self, agent_name: str) -> list[dict]:
        """Listet alle Versionen eines Agenten auf."""
        agent_path = self._get_agent_path(agent_name)
        if not self._agent_exists(agent_name):
            raise AgentNotFoundError(agent_name)
        
        version_manager = VersionManager(agent_path)
        return version_manager.list_versions()

    def delete_version(self, agent_name: str, version_id: str):
        """Löscht eine Version der Wissensbasis eines Agenten."""
        agent_path = self._get_agent_path(agent_name)
        if not self._agent_exists(agent_name):
            raise AgentNotFoundError(agent_name)
        
        version_manager = VersionManager(agent_path)
        version_manager.delete_version(version_id)
        print(f"Version '{version_id}' für Agent '{agent_name}' erfolgreich gelöscht.")

# --- 4. CLI Interface (argparse) ---

def main():
    parser = argparse.ArgumentParser(
        description="KnowledgeFlask CLI: Verwalte KI-Agenten, Wissensbasen und Versionen.",
        formatter_class=argparse.RawTextHelpFormatter # Behält Formatierung in Hilfetexten bei
    )
    
    # Globales Argument für das Basisverzeichnis (optional)
    parser.add_argument(
        "--base-dir", 
        default=KNOWLEDGE_FLASK_BASE_DIR, 
        help=f"Basisverzeichnis für KnowledgeFlask-Daten (Standard: {KNOWLEDGE_FLASK_BASE_DIR})"
    )

    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Befehle")

    # --- Agent Commands ---
    agent_parser = subparsers.add_parser("agent", help="Verwalte Agenten.")
    agent_subparsers = agent_parser.add_subparsers(dest="agent_command", help="Agenten-Operationen")

    # agent create
    agent_create_parser = agent_subparsers.add_parser("create", help="Erstelle einen neuen Agenten.")
    agent_create_parser.add_argument("name", help="Der Name des Agenten.")

    # agent delete
    agent_delete_parser = agent_subparsers.add_parser("delete", help="Lösche einen Agenten.")
    agent_delete_parser.add_argument("name", help="Der Name des zu löschenden Agenten.")

    # agent list
    agent_list_parser = agent_subparsers.add_parser("list", help="Liste alle Agenten auf.")

    # --- Knowledge Commands ---
    knowledge_parser = subparsers.add_parser("knowledge", help="Verwalte die Wissensbasis eines Agenten.")
    knowledge_subparsers = knowledge_parser.add_subparsers(dest="knowledge_command", help="Wissensbasis-Operationen")

    # knowledge add
    knowledge_add_parser = knowledge_subparsers.add_parser("add", help="Füge Wissen zu einem Agenten hinzu.")
    knowledge_add_parser.add_argument("agent_name", help="Der Name des Agenten.")
    knowledge_add_parser.add_argument("item", help="Das hinzuzufügende Wissenselement (Text).")

    # knowledge get
    knowledge_get_parser = knowledge_subparsers.add_parser("get", help="Zeige die Wissensbasis eines Agenten an.")
    knowledge_get_parser.add_argument("agent_name", help="Der Name des Agenten.")

    # --- Version Commands ---
    version_parser = subparsers.add_parser("version", help="Verwalte Versionen der Wissensbasis eines Agenten.")
    version_subparsers = version_parser.add_subparsers(dest="version_command", help="Versionierungs-Operationen")

    # version create
    version_create_parser = version_subparsers.add_parser("create", help="Erstelle eine neue Version der Wissensbasis.")
    version_create_parser.add_argument("agent_name", help="Der Name des Agenten.")
    version_create_parser.add_argument("-d", "--description", help="Eine Beschreibung für diese Version (optional).")

    # version restore
    version_restore_parser = version_subparsers.add_parser("restore", help="Stelle eine Version der Wissensbasis wieder her.")
    version_restore_parser.add_argument("agent_name", help="Der Name des Agenten.")
    version_restore_parser.add_argument("version_id", help="Die ID der wiederherzustellenden Version.")

    # version list
    version_list_parser = version_subparsers.add_parser("list", help="Liste alle Versionen eines Agenten auf.")
    version_list_parser.add_argument("agent_name", help="Der Name des Agenten.")

    # version delete
    version_delete_parser = version_subparsers.add_parser("delete", help="Lösche eine Version der Wissensbasis.")
    version_delete_parser.add_argument("agent_name", help="Der Name des Agenten.")
    version_delete_parser.add_argument("version_id", help="Die ID der zu löschenden Version.")

    args = parser.parse_args()

    # Wenn kein Unterbefehl angegeben wurde, zeige Hilfe
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    # Initialisiere die KnowledgeFlask-Anwendung
    try:
        kf_app = KnowledgeFlask(base_dir=args.base_dir)
    except KnowledgeFlaskException as e:
        print(f"Fehler beim Initialisieren von KnowledgeFlask: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.command == "agent":
            if args.agent_command == "create":
                kf_app.create_agent(args.name)
            elif args.agent_command == "delete":
                kf_app.delete_agent(args.name)
            elif args.agent_command == "list":
                agents = kf_app.list_agents()
                if agents:
                    print("Verfügbare Agenten:")
                    for agent in agents:
                        print(f"  - {agent}")
                else:
                    print("Keine Agenten gefunden.")
            else:
                agent_parser.print_help()
                sys.exit(1)

        elif args.command == "knowledge":
            if args.knowledge_command == "add":
                kf_app.add_knowledge(args.agent_name, args.item)
            elif args.knowledge_command == "get":
                knowledge = kf_app.get_knowledge(args.agent_name)
                if knowledge:
                    print(f"Wissensbasis für Agent '{args.agent_name}':")
                    for i, item in enumerate(knowledge):
                        print(f"  {i+1}. {item}")
                else:
                    print(f"Wissensbasis für Agent '{args.agent_name}' ist leer.")
            else:
                knowledge_parser.print_help()
                sys.exit(1)

        elif args.command == "version":
            if args.version_command == "create":
                kf_app.create_version(args.agent_name, args.description)
            elif args.version_command == "restore":
                kf_app.restore_version(args.agent_name, args.version_id)
            elif args.version_command == "list":
                versions = kf_app.list_versions(args.agent_name)
                if versions:
                    print(f"Versionen für Agent '{args.agent_name}':")
                    for version in versions:
                        print(f"  ID: {version.get('id', 'N/A')}")
                        print(f"    Zeitstempel: {version.get('timestamp', 'N/A')}")
                        print(f"    Beschreibung: {version.get('description', 'N/A')}")
                        print("-" * 20)
                else:
                    print(f"Keine Versionen für Agent '{args.agent_name}' gefunden.")
            elif args.version_command == "delete":
                kf_app.delete_version(args.agent_name, args.version_id)
            else:
                version_parser.print_help()
                sys.exit(1)

    except KnowledgeFlaskException as e:
        print(f"Fehler: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()


---

### So benutzt du den Code:

1.  **Speichern**: Speichere den Code als `knowledgeflask.py` (oder einen anderen Namen).
2.  **Ausführen (CLI)**: Öffne ein Terminal und navigiere in das Verzeichnis, in dem du die Datei gespeichert hast. Dann kannst du Befehle wie folgt ausführen:

    bash
    # Hilfe anzeigen
    python knowledgeflask.py --help
    python knowledgeflask.py agent --help
    python knowledgeflask.py knowledge --help
    python knowledgeflask.py version --help

    # Agenten erstellen
    python knowledgeflask.py agent create MeinErsterAgent
    python knowledgeflask.py agent create Assistent007

    # Agenten auflisten
    python knowledgeflask.py agent list

    # Wissen hinzufügen
    python knowledgeflask.py knowledge add MeinErsterAgent "Die Sonne ist ein Stern."
    python knowledgeflask.py knowledge add MeinErsterAgent "Erde dreht sich um die Sonne."
    python knowledgeflask.py knowledge add Assistent007 "KI lernt aus Daten."

    # Wissen eines Agenten anzeigen
    python knowledgeflask.py knowledge get MeinErsterAgent
    python knowledgeflask.py knowledge get Assistent007

    # Eine Version der Wissensbasis erstellen
    python knowledgeflask.py version create MeinErsterAgent -d "Wissen über Astronomie hinzugefügt."
    # Eine weitere Version nach Änderungen
    python knowledgeflask.py knowledge add MeinErsterAgent "Der Mond dreht sich um die Erde."
    python knowledgeflask.py version create MeinErsterAgent -d "Mondwissen hinzugefügt."

    # Versionen eines Agenten auflisten
    python knowledgeflask.py version list MeinErsterAgent

    # Eine spezifische Version wiederherstellen (ersetze <version_id> mit einer echten ID aus 'version list')
    # z.B. python knowledgeflask.py version restore MeinErsterAgent 123e4567-e89b-12d3-a456-426614174000

    # Eine Version löschen (ersetze <version_id>)
    # z.g. python knowledgeflask.py version delete MeinErsterAgent 123e4567-e89b-12d3-a456-426614174000

    # Agenten und alle Daten löschen
    python knowledgeflask.py agent delete MeinErsterAgent
    

### Erläuterungen und Features:

*   **Basisverzeichnis**: Alle Daten werden standardmäßig in einem `.knowledge_flask`-Verzeichnis in deinem Home-Verzeichnis gespeichert (`~/.knowledge_flask`). Du kannst dies mit `--base-dir` ändern.
*   **Fehlerbehandlung**: Jeder kritische Schritt ist in `try...except` Blöcke gehüllt. Eigene Exceptions (`AgentNotFoundError`, `AgentAlreadyExistsError`, `VersionNotFoundError`, `KnowledgeFlaskException`) werden für spezifische Fehlerfälle verwendet. Unerwartete Fehler werden abgefangen und führen zu einer aussagekräftigen Fehlermeldung und einem `sys.exit(1)`.
*   **`KnowledgeBaseManager`**:
    *   Verwendet `knowledge.json` als Liste von Strings.
    *   `add_knowledge` prüft auf Duplikate, bevor ein Element hinzugefügt wird.
    *   `_load_knowledge_from_file` und `_save_knowledge_to_file` kapseln den Dateizugriff und die Fehlerbehandlung für JSON.
*   **`VersionManager`**:
    *   Erstellt ein `versions`-Unterverzeichnis pro Agent.
    *   Jede Version bekommt eine eindeutige UUID und ein eigenes Verzeichnis mit einem Snapshot der `knowledge.json` und einer `version_meta.json` (für Zeitstempel und Beschreibung).
    *   `list_versions` sortiert die Versionen nach Zeitstempel (neueste zuerst).
    *   `restore_version` kopiert die Wissensbasis einer älteren Version zurück in die aktuelle.
*   **CLI mit `argparse`**: Die Kommandozeilenschnittstelle ist klar strukturiert mit Unterbefehlen für `agent`, `knowledge` und `version`, was eine intuitive Bedienung ermöglicht.
*   **Duplikate**: Beim Hinzufügen von Wissen wird geprüft, ob der exakte String bereits in der Wissensbasis vorhanden ist.

Dieser Code deckt alle deine genannten Punkte ab und bietet eine solide Grundlage für die weitere Entwicklung deines 'KnowledgeFlask'-Projekts!