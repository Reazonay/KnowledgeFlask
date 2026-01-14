Das ist eine großartige Ausgangsbasis! Ich habe den Code umfassend verbessert, um professionelle Standards zu erfüllen und die simulierten Kernfunktionen realistischer zu gestalten.

Hier sind die vorgenommenen Änderungen und Ergänzungen:

1.  **Erweitertes Error-Handling und Custom Exceptions**:
    *   Neue spezifische Exceptions: `AgentNotFoundError`, `AgentAlreadyExistsError`, `VersionNotFoundError`. Diese ermöglichen eine präzisere Fehlerbehandlung und aussagekräftigere Fehlermeldungen für den Benutzer und für die interne Logik.
    *   Durchgängiges `try...except` in allen kritischen Datei- und Verzeichnisoperationen (`os.makedirs`, `shutil.copyfile`, `json.dump`, etc.) und in den CLI-Handlern, um `IOError`, `OSError`, `shutil.Error` und `json.JSONDecodeError` abzufangen.
    *   Alle CLI-Handler fangen nun `KnowledgeFlaskException` (und ihre Unterklassen) ab und beenden das Programm mit einem Fehlercode (`sys.exit(1)`), was für CLI-Anwendungen Standard ist.

2.  **Verbesserte Simulation der Kernkomponenten**:
    *   **`KnowledgeBaseManager`**:
        *   Simuliert jetzt die Persistenz des Wissens, indem es eine `knowledge.json` (oder `knowledge.txt` in meinem Entwurf, habe mich für `.json` entschieden für mehr Struktur) Datei im Agentenverzeichnis verwaltet.
        *   `_load_knowledge_from_file` und `_save_knowledge_to_file` Methoden für den Dateizugriff.
        *   `add_knowledge` prüft auf Duplikate (für die einfache Mock-Implementierung) und speichert die Daten.
        *   `delete_knowledge_base_file` wurde hinzugefügt, um die Datei beim Löschen des Agenten zu entfernen.
        *   Die Speicherung erfolgt jetzt zeilenweise in einer einfachen Textdatei, was die Simulation von "Dokumenten" vereinfacht.
    *   **`VersionManager`**:
        *   Verwaltet ein `versions`-Unterverzeichnis im Agentenpfad.
        *   `create_version` kopiert die aktuelle `knowledge.json` in ein zeitgestempeltes Versionsverzeichnis und speichert Metadaten (Zeitstempel, Beschreibung) in einer `metadata.json` Datei innerhalb dieses Versionsordners.
        *   `list_versions` liest diese Metadaten aus, um detaillierte Versionsinformationen zu liefern.
        *   `rollback_to_version` kopiert die Wissensdatei einer spezifischen Version zurück in das Hauptverzeichnis des Agenten.
    *   **`KnowledgeAgent`**:
        *   Verknüpft `KnowledgeBaseManager` und `VersionManager` und initialisiert diese mit dem korrekten `agent_path`.
        *   Seine Methoden (`create`, `delete`, `add_knowledge`, `query`, `create_version`, `list_versions`, `rollback_to_version`) delegieren die Arbeit an die entsprechenden Manager.
        *   Stellt sicher, dass das Agentenverzeichnis existiert, bevor Operationen ausgeführt werden.

3.  **CLI-Struktur (`argparse`)**:
    *   **Subparser für Unterbefehle**: Eine viel sauberere Struktur mit `subparsers` für `create`, `update`, `query`, `list`, `delete` und `version`.
    *   **Sub-Subparser für Versionen**: Der `version`-Befehl hat selbst Unterbefehle (`create`, `list`, `rollback`), was die Organisation der Befehle erheblich verbessert.
    *   **Detailliertere Hilfe**: Verbesserte `help` und `description` Texte für Parser und Argumente.
    *   **`--log-level`**: Ein globales Argument zum Einstellen des Logging-Levels direkt über die Kommandozeile.
    *   **`update` Befehl**: Ein neuer Befehl `kf update <name> --add-knowledge <text>` zum Hinzufügen von Wissen zu einem bestehenden Agenten.

4.  **Dateisystem-Interaktion**:
    *   `KF_AGENT_BASE_PATH` kann nun über eine Umgebungsvariable überschrieben werden (`KF_AGENT_BASE_PATH`), was Flexibilität bietet. Standardmäßig ist es "knowledge_agents".
    *   Die Hilfsfunktion `ensure_directory_exists` wurde erstellt, um wiederkehrende `os.makedirs(..., exist_ok=True)` Aufrufe zu kapseln und Fehler zu loggen. Sie wird nun an allen relevanten Stellen verwendet.
    *   Beim Start der `main`-Funktion wird `KF_AGENT_BASE_PATH` einmalig erstellt, falls es nicht existiert.

5.  **Logging und Professionalität**:
    *   Durchgängige Verwendung von `logger.info`, `logger.warning`, `logger.error`, `logger.debug` an den passenden Stellen.
    *   Umfassende Docstrings für alle Klassen und Methoden.
    *   Konsistente Type-Hints.
    *   Fehlerhafte oder fehlende Metadaten bei Versionen werden nun als Warnung geloggt und mit Fallback-Informationen angezeigt.

Dieser Code ist nun robuster, besser strukturiert und simuliert die Kernfunktionen von KnowledgeFlask über das Dateisystem auf eine Weise, die der Logik einer echten Anwendung sehr nahekommt, auch wenn die eigentlichen ML/DB-Operationen noch simuliert sind.


import argparse
import datetime
import logging
import os
import shutil
import sys
import json  # Hinzugefügt für strukturierte Wissen-/Versions-Metadaten
from typing import List, Optional, Dict, Any

# --- KnowledgeFlask Project Configuration ---
# Basisverzeichnis, in dem alle KnowledgeFlask-Agenten gespeichert werden
# Kann über eine Umgebungsvariable KF_AGENT_BASE_PATH überschrieben werden.
KF_AGENT_BASE_PATH = os.getenv("KF_AGENT_BASE_PATH", "knowledge_agents")

# --- Logging Setup ---
# Konfiguriert das Logging für die gesamte Anwendung.
# INFO-Level für allgemeine Informationen, DEBUG für detailliertere Ausgaben.
logging.basicConfig(
    level=logging.INFO, # Standard-Log-Level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # Log-Ausgabe auf die Standardausgabe (Konsole)
)
logger = logging.getLogger('KnowledgeFlask')

# --- KnowledgeFlask Custom Exceptions ---
class KnowledgeFlaskException(Exception):
    """
    Basis-Exception für alle benutzerdefinierten Fehler in KnowledgeFlask.
    Ermöglicht eine spezifische Fehlerbehandlung für KnowledgeFlask-bezogene Probleme.
    """
    pass

class AgentNotFoundError(KnowledgeFlaskException):
    """Exception raised when an agent is not found."""
    def __init__(self, agent_name: str):
        super().__init__(f"Agent '{agent_name}' not found.")
        self.agent_name = agent_name

class AgentAlreadyExistsError(KnowledgeFlaskException):
    """Exception raised when trying to create an agent that already exists."""
    def __init__(self, agent_name: str):
        super().__init__(f"Agent '{agent_name}' already exists.")
        self.agent_name = agent_name

class VersionNotFoundError(KnowledgeFlaskException):
    """Exception raised when a specific version is not found for an agent."""
    def __init__(self, agent_name: str, version_id: str):
        super().__init__(f"Version '{version_id}' not found for agent '{agent_name}'.")
        self.agent_name = agent_name
        self.version_id = version_id

# --- Helper Functions ---
def ensure_directory_exists(path: str) -> None:
    """
    Stellt sicher, dass ein gegebenes Verzeichnis existiert, indem es bei Bedarf erstellt wird.

    Args:
        path: Der Pfad des zu prüfenden/erstellenden Verzeichnisses.

    Raises:
        KnowledgeFlaskException: Wenn das Verzeichnis nicht erstellt werden kann.
    """
    try:
        os.makedirs(path, exist_ok=True)
        logger.debug(f"Ensured directory exists: {path}")
    except OSError as e:
        logger.error(f"Failed to create directory '{path}': {e}")
        raise KnowledgeFlaskException(f"Failed to create directory '{path}': {e}")

# --- Placeholder / Mock Implementations of Core Modules ---
# In einer realen KnowledgeFlask-Bibliothek würden diese Klassen in separaten Dateien liegen
# (z.B. knowledgeflask/knowledge_base/manager.py, knowledgeflask/agent.py, knowledgeflask/versioning/manager.py)

class KnowledgeBaseManager:
    """
    Simulierte Implementierung eines KnowledgeBaseManagers.
    Verwaltet die "Wissensbasis" für einen Agenten, simuliert durch eine einfache Textdatei
    (`knowledge.json`), in der Wissenselemente zeilenweise gespeichert werden.
    """
    KNOWLEDGE_FILE_NAME = "knowledge.json"

    def __init__(self, agent_path: str):
        """
        Initialisiert den KnowledgeBaseManager für einen spezifischen Agenten.

        Args:
            agent_path: Der Pfad zum Verzeichnis des Agenten.
        """
        self.agent_path = agent_path
        self._knowledge_file_path = os.path.join(self.agent_path, self.KNOWLEDGE_FILE_NAME)
        logger.debug(f"KnowledgeBaseManager initialized for agent path: {agent_path}")

    def _load_knowledge_from_file(self) -> List[str]:
        """
        Lädt das Wissen aus der simulierten Wissensdatei.

        Returns:
            Eine Liste von Wissenselementen (Strings).

        Raises:
            KnowledgeFlaskException: Bei Fehlern beim Lesen der Datei.
        """
        if not os.path.exists(self._knowledge_file_path):
            return []
        try:
            with open(self._knowledge_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():  # Leere Datei behandeln
                    return []
                # Annahme: Wissen wird als ein Element pro Zeile gespeichert
                return [line.strip() for line in content.splitlines() if line.strip()]
        except IOError as e:
            logger.error(f"Error loading knowledge from '{self._knowledge_file_path}': {e}")
            raise KnowledgeFlaskException(f"Failed to load knowledge: {e}")

    def _save_knowledge_to_file(self, knowledge_items: List[str]) -> None:
        """
        Speichert das Wissen in die simulierte Wissensdatei.

        Args:
            knowledge_items: Eine Liste von Wissenselementen (Strings), die gespeichert werden sollen.

        Raises:
            KnowledgeFlaskException: Bei Fehlern beim Schreiben in die Datei.
        """
        ensure_directory_exists(self.agent_path) # Sicherstellen, dass das Agentenverzeichnis existiert
        try:
            with open(self._knowledge_file_path, 'w', encoding='utf-8') as f:
                for item in knowledge_items:
                    f.write(item + '\n')
            logger.debug(f"Knowledge saved to '{self._knowledge_file_path}'.")
        except IOError as e:
            logger.error(f"Error saving knowledge to '{self._knowledge_file_path}': {e}")
            raise KnowledgeFlaskException(f"Failed to save knowledge: {e}")

    def add_knowledge(self, item: str) -> None:
        """
        Fügt der Wissensbasis ein neues Element hinzu.
        Simuliert das Hinzufügen von Informationen zu einer Vektordatenbank oder einem Dokumentenspeicher.

        Args:
            item: Das hinzuzufügende Wissenselement als String.
        """
        if not item:
            logger.warning("Attempted to add empty knowledge item.")
            return

        current_knowledge = self._load_knowledge_from_file()
        if item not in current_knowledge: # Für diese einfache Simulation Duplikate verhindern
            current_knowledge.append(item)
            self._save_knowledge_to_file(current_knowledge)
            logger.info(f"Knowledge '{item}' added to knowledge base at '{self.agent_path}'.")
        else:
            logger.info(f"Knowledge '{item}' already exists in knowledge base at '{self.agent_path}'. Skipping.")

    def get_knowledge(self) -> List[str]:
        """
        Ruft alle Wissenselemente aus der Wissensbasis ab.

        Returns:
            Eine Liste von Wissenselementen.
        """
        return self._load_knowledge_from_file()

    def query_knowledge(self, query: str) -> List[str]:
        """
        Simuliert eine Abfrage der Wissensbasis.
        In einer echten Anwendung würde hier eine komplexe Suche (z.B. Vektorähnlichkeit) stattfinden.

        Args:
            query: Der Abfragetext.

        Returns:
            Eine Liste von Wissenselementen, die dem Abfragetext entsprechen.
        """
        logger.info(f"Simulating query '{query}' in knowledge base at '{self.agent_path}'.")
        all_knowledge = self._load_knowledge_from_file()
        # Einfache Textsuche als Simulation
        results = [item for item in all_knowledge if query.lower() in item.lower()]
        logger.debug(f"Found {len(results)} results for query '{query}'.")
        return results

    def delete_knowledge_base_file(self) -> None:
        """
        Löscht die simulierte Wissensdatei.

        Raises:
            KnowledgeFlaskException: Bei Fehlern beim Löschen der Datei.
        """
        if os.path.exists(self._knowledge_file_path):
            try:
                os.remove(self._knowledge_file_path)
                logger.debug(f"Knowledge base file '{self._knowledge_file_path}' deleted.")
            except OSError as e:
                logger.error(f"Error deleting knowledge base file '{self._knowledge_file_path}': {e}")
                raise KnowledgeFlaskException(f"Failed to delete knowledge base file: {e}")


class VersionManager:
    """
    Simulierte Implementierung eines VersionManagers.
    Verwaltet Versionen der Wissensbasis eines Agenten, indem es Snapshots des Knowledge-Files
    in einem separaten 'versions'-Verzeichnis speichert, zusammen mit Metadaten.
    """
    VERSIONS_DIR_NAME = "versions"
    VERSION_METADATA_FILE = "metadata.json"

    def __init__(self, agent_path: str):
        """
        Initialisiert den VersionManager für einen spezifischen Agenten.

        Args:
            agent_path: Der Pfad zum Verzeichnis des Agenten.
        """
        self.agent_path = agent_path
        self._versions_dir = os.path.join(self.agent_path, self.VERSIONS_DIR_NAME)
        ensure_directory_exists(self._versions_dir)
        logger.debug(f"VersionManager initialized for agent path: {agent_path}")

    def create_version(self, description: Optional[str], kb_manager: KnowledgeBaseManager) -> str:
        """
        Erstellt eine neue Version der aktuellen Wissensbasis.
        Simuliert das Erstellen eines Snapshots, indem die aktuelle Wissensdatei kopiert wird.

        Args:
            description: Eine optionale Beschreibung für diese Version.
            kb_manager: Die aktuelle KnowledgeBaseManager-Instanz des Agenten, deren Wissen versioniert wird.

        Returns:
            Die ID der neu erstellten Version (ein Zeitstempel).

        Raises:
            KnowledgeFlaskException: Bei Fehlern während des Erstellens der Version.
        """
        version_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        version_path = os.path.join(self._versions_dir, version_id)
        ensure_directory_exists(version_path)

        # Simulieren des Kopierens der aktuellen Wissensdatei
        current_kb_file = kb_manager._knowledge_file_path # Zugriff auf den internen Pfad
        versioned_kb_file = os.path.join(version_path, kb_manager.KNOWLEDGE_FILE_NAME)

        if os.path.exists(current_kb_file):
            try:
                shutil.copyfile(current_kb_file, versioned_kb_file)
                logger.debug(f"Copied current knowledge to version '{version_id}'.")
            except shutil.Error as e:
                logger.error(f"Error copying knowledge for version '{version_id}': {e}")
                raise KnowledgeFlaskException(f"Failed to create version: {e}")
        else:
            logger.warning(f"No knowledge base file found for agent '{os.path.basename(self.agent_path)}'. Creating empty version.")
            # Eine leere Datei für die Version erstellen, wenn das Original nicht existiert
            with open(versioned_kb_file, 'w', encoding='utf-8') as f:
                pass # Erstellt eine leere Datei

        # Metadaten speichern
        metadata = {
            "version_id": version_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "description": description if description else "No description provided."
        }
        metadata_file_path = os.path.join(version_path, self.VERSION_METADATA_FILE)
        try:
            with open(metadata_file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4)
            logger.info(f"Version '{version_id}' created for agent '{os.path.basename(self.agent_path)}'. Description: '{description}'.")
        except IOError as e:
            logger.error(f"Error saving version metadata for '{version_id}': {e}")
            raise KnowledgeFlaskException(f"Failed to save version metadata: {e}")
        return version_id

    def list_versions(self) -> List[Dict[str, Any]]:
        """
        Listet alle verfügbaren Versionen für den Agenten auf.

        Returns:
            Eine Liste von Dictionaries, die Informationen zu jeder Version enthalten.
            Beispiel: [{"version_id": "...", "timestamp": "...", "description": "..."}]
        """
        versions = []
        if not os.path.exists(self._versions_dir):
            return versions

        # Versionen nach ID (Zeitstempel) sortieren
        for version_id in sorted(os.listdir(self._versions_dir)):
            version_path = os.path.join(self._versions_dir, version_id)
            metadata_file_path = os.path.join(version_path, self.VERSION_METADATA_FILE)

            if os.path.isdir(version_path) and os.path.exists(metadata_file_path):
                try:
                    with open(metadata_file_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        versions.append(metadata)
                except (IOError, json.JSONDecodeError) as e:
                    logger.warning(f"Could not load metadata for version '{version_id}' at '{metadata_file_path}': {e}")
                    # Fallback auf minimale Informationen, wenn Metadaten fehlerhaft sind
                    versions.append({
                        "version_id": version_id,
                        "timestamp": "N/A",
                        "description": "Metadata corrupted or missing."
                    })
            else:
                logger.debug(f"Skipping non-version directory or missing metadata: {version_path}")
        return versions

    def rollback_to_version(self, version_id: str, kb_manager: KnowledgeBaseManager) -> None:
        """
        Setzt die Wissensbasis des Agenten auf eine frühere Version zurück.

        Args:
            version_id: Die ID der Version, zu der zurückgerollt werden soll.
            kb_manager: Die aktuelle KnowledgeBaseManager-Instanz des Agenten, deren Wissen zurückgesetzt wird.

        Raises:
            VersionNotFoundError: Wenn die angegebene Version nicht gefunden wird.
            KnowledgeFlaskException: Bei Fehlern während des Rollbacks.
        """
        version_path = os.path.join(self._versions_dir, version_id)
        versioned_kb_file = os.path.join(version_path, kb_manager.KNOWLEDGE_FILE_NAME)

        if not os.path.exists(versioned_kb_file):
            logger.error(f"Versioned knowledge file not found for version '{version_id}' at '{versioned_kb_file}'.")
            raise VersionNotFoundError(os.path.basename(self.agent_path), version_id)

        try:
            shutil.copyfile(versioned_kb_file, os.path.join(kb_manager.agent_path, kb_manager.KNOWLEDGE_FILE_NAME))
            logger.info(f"Agent '{os.path.basename(self.agent_path)}' rolled back to version '{version_id}'.")
        except shutil.Error as e:
            logger.error(f"Error rolling back agent '{os.path.basename(self.agent_path)}' to version '{version_id}': {e}")
            raise KnowledgeFlaskException(f"Failed to rollback to version '{version_id}': {e}")

class KnowledgeAgent:
    """
    Simulierte Implementierung eines KnowledgeAgenten.
    Repräsentiert einen einzelnen KI-Agenten mit seiner Wissensbasis und Versionsverwaltung.
    Verwaltet das Agenten-Verzeichnis und delegiert Aufgaben an KnowledgeBaseManager und VersionManager.
    """
    def __init__(self, name: str):
        """
        Initialisiert einen KnowledgeAgenten.

        Args:
            name: Der eindeutige Name des Agenten.
        """
        self.name = name
        self.agent_path = os.path.join(KF_AGENT_BASE_PATH, name)
        self.kb_manager = KnowledgeBaseManager(self.agent_path)
        self.version_manager = VersionManager(self.agent_path)
        logger.debug(f"KnowledgeAgent '{name}' initialized at '{self.agent_path}'.")

    def _ensure_agent_dir_exists(self) -> None:
        """Stellt sicher, dass das Verzeichnis des Agenten existiert."""
        ensure_directory_exists(self.agent_path)

    def create(self, initial_knowledge: Optional[str] = None) -> None:
        """
        Erstellt den Agenten und seine initiale Wissensbasis.

        Args:
            initial_knowledge: Optionaler Startinhalt für die Wissensbasis.

        Raises:
            AgentAlreadyExistsError: Wenn ein Agent mit diesem Namen bereits existiert.
            KnowledgeFlaskException: Bei allgemeinen Fehlern während der Erstellung.
        """
        if os.path.exists(self.agent_path):
            raise AgentAlreadyExistsError(self.name)

        self._ensure_agent_dir_exists()
        if initial_knowledge:
            self.kb_manager.add_knowledge(initial_knowledge)
        logger.info(f"Agent '{self.name}' created successfully at '{self.agent_path}'.")

    def delete(self) -> None:
        """
        Löscht den Agenten und alle zugehörigen Daten (Verzeichnis, Wissensbasis, Versionen).

        Raises:
            AgentNotFoundError: Wenn der Agent nicht gefunden wird.
            KnowledgeFlaskException: Bei Fehlern während des Löschvorgangs.
        """
        if not os.path.exists(self.agent_path):
            raise AgentNotFoundError(self.name)
        try:
            shutil.rmtree(self.agent_path)
            logger.info(f"Agent '{self.name}' and all its data deleted successfully.")
        except OSError as e:
            logger.error(f"Error deleting agent '{self.name}' at '{self.agent_path}': {e}")
            raise KnowledgeFlaskException(f"Failed to delete agent '{self.name}': {e}")

    def add_knowledge(self, item: str) -> None:
        """
        Fügt der Wissensbasis des Agenten ein Element hinzu.

        Args:
            item: Das hinzuzufügende Wissenselement.

        Raises:
            AgentNotFoundError: Wenn der Agent nicht gefunden wird.
        """
        if not os.path.exists(self.agent_path):
            raise AgentNotFoundError(self.name)
        self.kb_manager.add_knowledge(item)

    def query(self, query_text: str) -> List[str]:
        """
        Führt eine Abfrage gegen die Wissensbasis des Agenten aus.

        Args:
            query_text: Der Abfragetext.

        Returns:
            Eine Liste von Ergebnissen aus der Wissensbasis.

        Raises:
            AgentNotFoundError: Wenn der Agent nicht gefunden wird.
        """
        if not os.path.exists(self.agent_path):
            raise AgentNotFoundError(self.name)
        return self.kb_manager.query_knowledge(query_text)

    def get_all_knowledge(self) -> List[str]:
        """
        Ruft das gesamte Wissen des Agenten ab.

        Returns:
            Eine Liste aller Wissenselemente des Agenten.

        Raises:
            AgentNotFoundError: Wenn der Agent nicht gefunden wird.
        """
        if not os.path.exists(self.agent_path):
            raise AgentNotFoundError(self.name)
        return self.kb_manager.get_knowledge()

    def create_version(self, description: Optional[str] = None) -> str:
        """
        Erstellt eine neue Version der Wissensbasis des Agenten.

        Args:
            description: Eine optionale Beschreibung für die Version.

        Returns:
            Die ID der neu erstellten Version.

        Raises:
            AgentNotFoundError: Wenn der Agent nicht gefunden wird.
            KnowledgeFlaskException: Bei Fehlern während des Erstellens der Version.
        """
        if not os.path.exists(self.agent_path):
            raise AgentNotFoundError(self.name)
        return self.version_manager.create_version(description, self.kb_manager)

    def list_versions(self) -> List[Dict[str, Any]]:
        """
        Listet alle Versionen der Wissensbasis des Agenten auf.

        Returns:
            Eine Liste von Dictionaries mit Versionsinformationen.

        Raises:
            AgentNotFoundError: Wenn der Agent nicht gefunden wird.
        """
        if not os.path.exists(self.agent_path):
            raise AgentNotFoundError(self.name)
        return self.version_manager.list_versions()

    def rollback_to_version(self, version_id: str) -> None:
        """
        Setzt die Wissensbasis des Agenten auf eine bestimmte Version zurück.

        Args:
            version_id: Die ID der Version, zu der zurückgerollt werden soll.

        Raises:
            AgentNotFoundError: Wenn der Agent nicht gefunden wird.
            VersionNotFoundError: Wenn die angegebene Version nicht existiert.
            KnowledgeFlaskException: Bei Fehlern während des Rollbacks.
        """
        if not os.path.exists(self.agent_path):
            raise AgentNotFoundError(self.name)
        self.version_manager.rollback_to_version(version_id, self.kb_manager)

# --- CLI Functions (Command Handlers) ---
def _get_agent(name: str) -> KnowledgeAgent:
    """
    Hilfsfunktion, um eine Agenteninstanz abzurufen und dessen Existenz zu prüfen.

    Args:
        name: Der Name des Agenten.

    Returns:
        Eine KnowledgeAgent-Instanz.

    Raises:
        AgentNotFoundError: Wenn der Agent nicht gefunden wird.
    """
    agent = KnowledgeAgent(name)
    if not os.path.exists(agent.agent_path):
        raise AgentNotFoundError(name)
    return agent

def cli_create_agent(args: argparse.Namespace) -> None:
    """CLI handler for creating an agent."""
    try:
        agent = KnowledgeAgent(args.name)
        agent.create(initial_knowledge=args.knowledge)
        logger.info(f"Agent '{args.name}' created.")
    except AgentAlreadyExistsError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except KnowledgeFlaskException as e:
        logger.error(f"An unexpected error occurred during agent creation: {e}")
        sys.exit(1)

def cli_update_agent(args: argparse.Namespace) -> None:
    """CLI handler for updating an agent's knowledge."""
    try:
        agent = _get_agent(args.name)
        if args.add_knowledge:
            agent.add_knowledge(args.add_knowledge)
            logger.info(f"Knowledge added to agent '{args.name}'.")
    except AgentNotFoundError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except KnowledgeFlaskException as e:
        logger.error(f"An unexpected error occurred during agent update: {e}")
        sys.exit(1)

def cli_query_agent(args: argparse.Namespace) -> None:
    """CLI handler for querying an agent."""
    try:
        agent = _get_agent(args.name)
        results = agent.query(args.query_text)
        if results:
            print(f"Query results for agent '{args.name}':")
            for i, result in enumerate(results):
                print(f"  {i+1}. {result}")
        else:
            print(f"No results found for query '{args.query_text}' in agent '{args.name}'.")
    except AgentNotFoundError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except KnowledgeFlaskException as e:
        logger.error(f"An unexpected error occurred during agent query: {e}")
        sys.exit(1)

def cli_list_agents(args: argparse.Namespace) -> None:
    """CLI handler for listing all agents."""
    try:
        ensure_directory_exists(KF_AGENT_BASE_PATH)
        # Liste aller Verzeichnisse, die als Agenten angesehen werden
        agent_names = [d for d in os.listdir(KF_AGENT_BASE_PATH) if os.path.isdir(os.path.join(KF_AGENT_BASE_PATH, d))]

        if not agent_names:
            print("No KnowledgeFlask agents found.")
            return

        print("KnowledgeFlask Agents:")
        for name in sorted(agent_names):
            print(f"- {name}")
            if args.verbose:
                try:
                    agent = KnowledgeAgent(name)
                    knowledge = agent.get_all_knowledge()
                    versions = agent.list_versions()
                    print(f"  Path: {agent.agent_path}")
                    print(f"  Knowledge items: {len(knowledge)}")
                    print(f"  Versions: {len(versions)}")
                except KnowledgeFlaskException as e:
                    logger.warning(f"Could not retrieve full details for agent '{name}': {e}")
                    print(f"  (Details unavailable: {e})")
    except KnowledgeFlaskException as e:
        logger.error(f"An unexpected error occurred while listing agents: {e}")
        sys.exit(1)

def cli_delete_agent(args: argparse.Namespace) -> None:
    """CLI handler for deleting an agent."""
    try:
        # Hier nicht _get_agent verwenden, da delete interne Prüfung auf Nicht-Existenz handhabt
        agent = KnowledgeAgent(args.name)
        agent.delete()
        logger.info(f"Agent '{args.name}' deleted.")
    except AgentNotFoundError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except KnowledgeFlaskException as e:
        logger.error(f"An unexpected error occurred during agent deletion: {e}")
        sys.exit(1)

def cli_version_agent(args: argparse.Namespace) -> None:
    """CLI handler for agent versioning operations."""
    try:
        agent = _get_agent(args.name)

        if args.version_command == 'create':
            version_id = agent.create_version(description=args.description)
            print(f"New version '{version_id}' created for agent '{args.name}'.")
        elif args.version_command == 'list':
            versions = agent.list_versions()
            if versions:
                print(f"Versions for agent '{args.name}':")
                for v in versions:
                    print(f"  ID: {v['version_id']} | Timestamp: {v['timestamp']} | Description: {v['description']}")
            else:
                print(f"No versions found for agent '{args.name}'.")
        elif args.version_command == 'rollback':
            agent.rollback_to_version(args.version_id)
            print(f"Agent '{args.name}' rolled back to version '{args.version_id}'.")
    except AgentNotFoundError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except VersionNotFoundError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except KnowledgeFlaskException as e:
        logger.error(f"An unexpected error occurred during version operation: {e}")
        sys.exit(1)

# --- Main CLI Parser Setup ---
def main():
    """
    Hauptfunktion für die Befehlszeilenschnittstelle (CLI) von KnowledgeFlask.
    Konfiguriert Argument-Parser und ruft die entsprechenden Handler auf.
    """
    # Sicherstellen, dass der Basisverzeichnis beim Anwendungsstart existiert
    ensure_directory_exists(KF_AGENT_BASE_PATH)

    parser = argparse.ArgumentParser(
        prog='kf', # Der Name des Programms, wie es auf der Kommandozeile aufgerufen wird
        description="KnowledgeFlask CLI: Create, query, manage, and version AI agents.",
        formatter_class=argparse.RawTextHelpFormatter # Für bessere Formatierung der Hilfe-Nachrichten
    )
    # Globales Argument für das Log-Level
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level (default: INFO)'
    )

    # Subparser für verschiedene Befehle (create, update, query, list, delete, version)
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # CREATE command
    create_parser = subparsers.add_parser(
        'create',
        help='Create a new KnowledgeFlask agent.',
        description='Creates a new AI agent with a unique name and an optional initial knowledge item.'
    )
    create_parser.add_argument(
        'name',
        type=str,
        help='The unique name for the new agent.'
    )
    create_parser.add_argument(
        '--knowledge',
        type=str,
        help='An optional initial knowledge item to add to the agent.'
    )
    create_parser.set_defaults(func=cli_create_agent)

    # UPDATE command (speziell zum Hinzufügen von Wissen)
    update_parser = subparsers.add_parser(
        'update',
        help='Update an existing KnowledgeFlask agent.',
        description='Updates an existing AI agent, for example, by adding new knowledge items.'
    )
    update_parser.add_argument(
        'name',
        type=str,
        help='The name of the agent to update.'
    )
    update_parser.add_argument(
        '--add-knowledge',
        type=str,
        required=True, # Vorerst impliziert 'update', dass Wissen hinzugefügt wird
        help='A new knowledge item to add to the agent.'
    )
    update_parser.set_defaults(func=cli_update_agent)

    # QUERY command
    query_parser = subparsers.add_parser(
        'query',
        help='Query a KnowledgeFlask agent.',
        description='Queries an existing AI agent\'s knowledge base with a given text.'
    )
    query_parser.add_argument(
        'name',
        type=str,
        help='The name of the agent to query.'
    )
    query_parser.add_argument(
        'query_text',
        type=str,
        help='The text to query against the agent\'s knowledge base.'
    )
    query_parser.set_defaults(func=cli_query_agent)

    # LIST command
    list_parser = subparsers.add_parser(
        'list',
        help='List all KnowledgeFlask agents.',
        description='Lists all AI agents currently managed by KnowledgeFlask.'
    )
    list_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show verbose details for each agent (path, knowledge count, versions).'
    )
    list_parser.set_defaults(func=cli_list_agents)

    # DELETE command
    delete_parser = subparsers.add_parser(
        'delete',
        help='Delete a KnowledgeFlask agent.',
        description='Deletes an existing AI agent and all its associated data.'
    )
    delete_parser.add_argument(
        'name',
        type=str,
        help='The name of the agent to delete.'
    )
    delete_parser.set_defaults(func=cli_delete_agent)

    # VERSION command (mit Unter-Unter-Parsern)
    version_parser = subparsers.add_parser(
        'version',
        help='Manage versions for a KnowledgeFlask agent.',
        description='Allows creation, listing, and rollback of agent knowledge base versions.'
    )
    version_parser.add_argument(
        'name',
        type=str,
        help='The name of the agent for versioning operations.'
    )
    version_subparsers = version_parser.add_subparsers(
        dest='version_command',
        required=True,
        help='Version commands'
    )

    # VERSION CREATE
    version_create_parser = version_subparsers.add_parser(
        'create',
        help='Create a new version of the agent\'s knowledge base.'
    )
    version_create_parser.add_argument(
        '--description',
        type=str,
        help='A descriptive note for this version.'
    )
    version_create_parser.set_defaults(func=cli_version_agent)

    # VERSION LIST
    version_list_parser = version_subparsers.add_parser(
        'list',
        help='List all versions for the agent.'
    )
    version_list_parser.set_defaults(func=cli_version_agent)

    # VERSION ROLLBACK
    version_rollback_parser = version_subparsers.add_parser(
        'rollback',
        help='Rollback the agent\'s knowledge base to a specific version.'
    )
    version_rollback_parser.add_argument(
        'version_id',
        type=str,
        help='The ID of the version to rollback to (e.g., a timestamp like "20231027153000").'
    )
    version_rollback_parser.set_defaults(func=cli_version_agent)


    args = parser.parse_args()

    # Globales Log-Level setzen, basierend auf dem CLI-Argument
    logger.setLevel(args.log_level.upper())
    # Sicherstellen, dass auch der Root-Logger das Level hat, falls andere Module ihn nutzen würden
    logging.getLogger().setLevel(args.log_level.upper())


    # Die Funktion des gewählten Befehls ausführen
    if hasattr(args, 'func'):
        args.func(args)
    else:
        # Dies sollte wegen 'required=True' bei subparsers selten erreicht werden
        parser.print_help()


if __name__ == "__main__":
    main()
