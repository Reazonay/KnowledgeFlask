Als KI-Projektleiter baue ich nun das `main.py` für 'KnowledgeFlask'. Es wird eine Befehlszeilenschnittstelle (CLI) bereitstellen, um die Kernfunktionen des Toolkits zu demonstrieren: Agenten erstellen, abfragen, auflisten und versionieren.

Da das Projekt umfangreich ist und die Implementierung von Machine-Learning-Modellen, Vektordatenbanken und Dateiverwaltung in separate Module ausgelagert werden müsste, werde ich für dieses `main.py` **simulierte Implementierungen** der Kernkomponenten (`KnowledgeBaseManager`, `KnowledgeAgent`, `VersionManager`) direkt im `main.py` bereitstellen. Diese Platzhalter zeigen die Schnittstelle und die erwartete Logik auf, würden aber in einer echten Anwendung durch voll funktionsfähige Module ersetzt.

Professionelle Merkmale wie Logging, umfassendes Error-Handling, Docstrings und Type-Hints werden durchgängig angewendet.


import argparse
import datetime
import logging
import os
import shutil
import sys
from typing import List, Optional

# --- KnowledgeFlask Project Configuration ---
# Basisverzeichnis, in dem alle KnowledgeFlask-Agenten gespeichert werden
KF_AGENT_BASE_PATH = "knowledge_agents"

# --- Logging Setup ---
# Konfiguriert das Logging für die gesamte Anwendung.
# INFO-Level für allgemeine Informationen, DEBUG für detailliertere Ausgaben.
logging.basicConfig(
    level=logging.INFO,
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

# --- Placeholder / Mock Implementations of Core Modules ---
# In einer realen KnowledgeFlask-Bibliothek würden diese Klassen in separaten Dateien liegen
# (z.B. knowledgeflask/knowledge_base.py, knowledgeflask/agent.py, knowledgeflask/versioning.py).
# Hier dienen sie dazu, die Struktur und Interaktion innerhalb von main.py zu demonstrieren.

class KnowledgeBaseManager:
    """
    Simulierte Klasse zur Verwaltung einer domänenspezifischen Wissensbasis.
    Verantwortlich für das Erstellen, Laden und Aktualisieren der Wissensbasis
    aus Datensätzen.
    """
    def __init__(self, agent_name: str, base_path: str = KF_AGENT_BASE_PATH):
        """
        Initialisiert den KnowledgeBaseManager für einen spezifischen Agenten.

        Args:
            agent_name (str): Der eindeutige Name des KI-Agenten.
            base_path (str): Das Basisverzeichnis für alle Agenten.
        """
        self.agent_path = os.path.join(base_path, agent_name)
        self.kb_path = os.path.join(self.agent_path, "knowledge_base")
        os.makedirs(self.kb_path, exist_ok=True) # Sicherstellen, dass das Verzeichnis existiert
        logger.debug(f"KnowledgeBaseManager für Agent '{agent_name}' initialisiert.")

    def create_from_data(self, data_sources: List[str], chunk_size: int = 500, overlap: int = 50) -> bool:
        """
        Simuliert die Erstellung einer Wissensbasis aus bereitgestellten Datenquellen.

        In einer echten Implementierung würde dies die folgenden Schritte umfassen:
        1.  **Datenladen**: Einlesen von Text, PDF, Markdown etc.
        2.  **Text-Chunking**: Teilen langer Dokumente in kleinere, handhabbare Stücke.
        3.  **Einbetten (Embedding)**: Umwandlung der Text-Chunks in Vektor-Embeddings
            mithilfe eines lokalen Sprachmodells (z.B. Sentence Transformers).
        4.  **Speichern**: Ablegen der Embeddings in einem Vektorspeicher (z.B. FAISS, ChromaDB, Weaviate).

        Args:
            data_sources (List[str]): Eine Liste von Pfaden zu den Quelldateien oder -verzeichnissen.
            chunk_size (int): Die maximale Größe der Text-Chunks in Zeichen.
            overlap (int): Die Überlappung zwischen aufeinanderfolgenden Text-Chunks.

        Returns:
            bool: True, wenn die Wissensbasis erfolgreich erstellt oder aktualisiert wurde.

        Raises:
            KnowledgeFlaskException: Wenn ein Fehler während des Erstellungsprozesses auftritt.
        """
        logger.info(f"Simuliere Erstellung der Wissensbasis aus {len(data_sources)} Quellen...")
        logger.debug(f"Datenquellen: {data_sources}, Chunk-Größe: {chunk_size}, Überlappung: {overlap}")
        
        try:
            # Simulierte Datenverarbeitung und Speicherung
            processed_files = []
            for source in data_sources:
                # Hier würde die tatsächliche Logik zum Laden, Parsen, Chunking und Embedding erfolgen
                logger.debug(f"Verarbeite simulierte Datenquelle: {source}")
                processed_files.append(os.path.basename(source))

            # Simulierte Speicherung eines Manifests oder Index
            manifest_path = os.path.join(self.kb_path, "kb_manifest.json")
            with open(manifest_path, "w") as f:
                f.write(f"{{\n  \"created_at\": \"{datetime.datetime.now().isoformat()}\",\n")
                f.write(f"  \"data_sources\": {processed_files},\n")
                f.write(f"  \"chunk_size\": {chunk_size},\n")
                f.write(f"  \"overlap\": {overlap},\n")
                f.write(f"  \"status\": \"simulated_ready\"\n}}")
            
            # Simulierte Erstellung von Dummy-Vektorspeicherdateien
            with open(os.path.join(self.kb_path, "vector_store.bin"), "w") as f:
                f.write("Simulated vector store data.")
            with open(os.path.join(self.kb_path, "embedding_model_config.json"), "w") as f:
                f.write("Simulated embedding model config.")

            logger.info(f"Wissensbasis erfolgreich erstellt/aktualisiert unter {self.kb_path}.")
            return True
        except Exception as e:
            logger.error(f"Fehler bei der Erstellung der Wissensbasis: {e}", exc_info=True)
            raise KnowledgeFlaskException(f"Fehler bei der KB-Erstellung für Agent '{os.path.basename(self.agent_path)}': {e}")

    def load_knowledge_base(self) -> bool:
        """
        Simuliert das Laden einer vorhandenen Wissensbasis.

        In einer echten Implementierung würde dies das Laden des Vektorspeichers
        und des Embedding-Modells umfassen.

        Returns:
            bool: True, wenn die Wissensbasis erfolgreich geladen wurde.

        Raises:
            KnowledgeFlaskException: Wenn die Wissensbasis nicht gefunden wird oder ein Ladefehler auftritt.
        """
        manifest_path = os.path.join(self.kb_path, "kb_manifest.json")
        if not os.path.exists(manifest_path):
            raise KnowledgeFlaskException(f"Wissensbasis-Manifest nicht gefunden unter {self.kb_path}. Agent möglicherweise nicht erstellt.")
        
        # Simulierte Ladeoperationen
        if not os.path.exists(os.path.join(self.kb_path, "vector_store.bin")):
             raise KnowledgeFlaskException(f"Simulierter Vektorspeicher nicht gefunden unter {self.kb_path}.")

        logger.info(f"Wissensbasis erfolgreich geladen von {self.kb_path}.")
        return True # In einem realen Szenario würde dies das Vektorspeicherobjekt zurückgeben

class KnowledgeAgent:
    """
    Simulierte Klasse, die einen domänenspezifischen KI-Wissensagenten repräsentiert.
    Kombiniert eine Wissensbasis mit einem Abfragemechanismus (z.B. RAG unter Verwendung
    eines lokalen LLM oder eines API-basierten).
    """
    def __init__(self, agent_name: str, kb_manager: KnowledgeBaseManager):
        """
        Initialisiert den KnowledgeAgent.

        Args:
            agent_name (str): Der Name des Agenten.
            kb_manager (KnowledgeBaseManager): Eine Instanz des KnowledgeBaseManagers.
        """
        self.name = agent_name
        self.kb_manager = kb_manager
        self.knowledge_base = None # Würde den tatsächlichen geladenen Vektorspeicher enthalten
        self.llm = None # Platzhalter für ein lokales LLM oder API-Wrapper
        logger.debug(f"KnowledgeAgent '{agent_name}' initialisiert.")

    def load(self) -> None:
        """
        Lädt die zugehörige Wissensbasis und initialisiert optional ein LLM.

        Raises:
            KnowledgeFlaskException: Wenn die Wissensbasis nicht geladen werden kann.
        """
        logger.info(f"Lade Agent '{self.name}'...")
        try:
            self.knowledge_base = self.kb_manager.load_knowledge_base()
            # Hier würde die Initialisierung eines lokalen LLM-Modells erfolgen
            # (z.B. mit HuggingFace transformers oder llama-cpp-python).
            self.llm = "Simulated Local LLM (e.g., Llama 2, Mistral)" 
            logger.info(f"Agent '{self.name}' erfolgreich geladen.")
        except KnowledgeFlaskException as e:
            logger.error(f"Fehler beim Laden von Agent '{self.name}': {e}")
            raise

    def query(self, question: str, top_k: int = 3) -> str:
        """
        Fragt den Agenten mit einer gegebenen Frage ab.

        Dies würde typischerweise die folgenden Schritte umfassen:
        1.  **Frage einbetten**: Umwandlung der Frage in ein Vektor-Embedding.
        2.  **Dokumentenabruf (Retrieval)**: Abrufen der relevantesten Dokumente
            aus der Wissensbasis basierend auf der Ähnlichkeit der Embeddings (RAG - Retrieval Augmented Generation).
        3.  **Prompt-Konstruktion**: Erstellen eines Prompts für das LLM,
            der die Frage und die abgerufenen relevanten Dokumente als Kontext enthält.
        4.  **LLM-Interaktion**: Aufrufen des LLM, um eine Antwort zu generieren.

        Args:
            question (str): Die an den Agenten zu stellende Frage.
            top_k (int): Die Anzahl der Top-Dokumente, die aus der Wissensbasis abgerufen werden sollen.

        Returns:
            str: Die generierte Antwort des Agenten.

        Raises:
            KnowledgeFlaskException: Wenn der Agent nicht geladen ist oder ein Fehler während der Abfrage auftritt.
        """
        if not self.knowledge_base or not self.llm:
            raise KnowledgeFlaskException("Agent nicht geladen. Bitte .load() aufrufen, bevor abgefragt wird.")
        
        logger.info(f"Frage Agent '{self.name}' mit: '{question}' (Top-K: {top_k})")
        try:
            # Simulierte Abruf- und LLM-Interaktion
            # 1. Frage einbetten (simuliert)
            # 2. Relevante Dokumente abrufen (simuliert)
            retrieved_docs = [
                f"Simuliertes Dokument 1: Kontext über '{question}' aus der Domäne '{self.name}'.",
                f"Simuliertes Dokument 2: Weitere relevante Informationen zu '{question}'.",
                f"Simuliertes Dokument 3: Detailliertere Erläuterung.",
            ][:top_k] # Beschränken auf top_k simulierte Dokumente
            logger.debug(f"Abgerufene simulierte Dokumente: {retrieved_docs}")

            # 3. Prompt mit Kontext konstruieren (simuliert)
            context = "\n".join(retrieved_docs)
            
            # 4. LLM aufrufen (simuliert)
            simulated_answer = (
                f"Basierend auf der Wissensbasis von '{self.name}' und Ihrer Frage '{question}', "
                f"habe ich folgende relevante Informationen gefunden:\n---\n{context}\n---\n"
                f"Daraus ergibt sich die folgende simulierte Antwort: 'Dies ist eine detaillierte "
                f"simulierte Antwort auf die Frage \"{question}\", die sich auf die bereitgestellten "
                f"Informationen stützt und die Besonderheiten der Domäne '{self.name}' berücksichtigt.'"
            )
            return simulated_answer
        except Exception as e:
            logger.error(f"Fehler bei der Abfrage für Agent '{self.name}': {e}", exc_info=True)
            raise KnowledgeFlaskException(f"Fehler bei der Abfrage für Agent '{self.name}': {e}")

class VersionManager:
    """
    Simulierte Klasse zur Verwaltung von Versionen der Wissensbasis eines Agenten.
    Ermöglicht das Erstellen von Snapshots, Auflisten von Versionen und Rollback zu früheren Ständen.
    """
    def __init__(self, agent_name: str, base_path: str = KF_AGENT_BASE_PATH):
        """
        Initialisiert den VersionManager für einen spezifischen Agenten.

        Args:
            agent_name (str): Der Name des Agenten.
            base_path (str): Das Basisverzeichnis für alle Agenten.
        """
        self.agent_path = os.path.join(base_path, agent_name)
        self.versions_path = os.path.join(self.agent_path, "versions")
        os.makedirs(self.versions_path, exist_ok=True)
        logger.debug(f"VersionManager für Agent '{agent_name}' initialisiert unter {self.versions_path}.")

    def _get_current_kb_path(self) -> str:
        """Hilfsfunktion zur Ermittlung des Pfades der aktuellen Wissensbasis."""
        return os.path.join(self.agent_path, "knowledge_base")

    def create_snapshot(self, version_tag: Optional[str] = None) -> str:
        """
        Erstellt einen versionierten Snapshot der aktuellen Wissensbasis des Agenten.

        Args:
            version_tag (Optional[str]): Ein optionaler benutzerdefinierter Tag für den Snapshot.
                                         Wird automatisch generiert, wenn nicht angegeben.

        Returns:
            str: Der verwendete Versionstag des erstellten Snapshots.

        Raises:
            KnowledgeFlaskException: Wenn keine aktuelle Wissensbasis zum Snapshot gefunden wird
                                     oder ein Fehler beim Kopieren auftritt.
        """
        if version_tag is None:
            # Generiere einen standardmäßigen, zeitgestempelten Versionstag
            version_tag = f"snapshot_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        snapshot_path = os.path.join(self.versions_path, version_tag)
        current_kb_path = self._get_current_kb_path()

        if not os.path.exists(current_kb_path) or not os.listdir(current_kb_path):
            raise KnowledgeFlaskException(f"Keine aktuelle Wissensbasis gefunden unter {current_kb_path} zum Snapshot.")
        
        if os.path.exists(snapshot_path):
            logger.warning(f"Snapshot-Pfad '{snapshot_path}' existiert bereits. Überschreibe bestehenden Snapshot.")
            shutil.rmtree(snapshot_path) # Vor dem Kopieren bestehenden Snapshot löschen

        try:
            # Simuliertes Kopieren der aktuellen KB in das Versionierungsverzeichnis
            # In einer realen Implementierung würde hier das Kopieren der Vektorspeicherdateien erfolgen.
            shutil.copytree(current_kb_path, snapshot_path)
            
            # Füge Snapshot-Metadaten hinzu
            with open(os.path.join(snapshot_path, "snapshot_metadata.json"), "w") as f:
                f.write(f"{{\n  \"version_tag\": \"{version_tag}\",\n")
                f.write(f"  \"created_at\": \"{datetime.datetime.now().isoformat()}\",\n")
                f.write(f"  \"source_kb\": \"{os.path.basename(current_kb_path)}\"\n}}")
            
            logger.info(f"Snapshot '{version_tag}' erfolgreich erstellt unter {snapshot_path}")
            return version_tag
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Snapshots '{version_tag}' für Agent '{os.path.basename(self.agent_path)}': {e}", exc_info=True)
            raise KnowledgeFlaskException(f"Fehler bei der Versionierung (Snapshot): {e}")

    def list_versions(self) -> List[str]:
        """
        Listet alle verfügbaren Versionen (Snapshots) für den Agenten auf.

        Returns:
            List[str]: Eine Liste von Versionstags.

        Raises:
            KnowledgeFlaskException: Wenn ein Fehler beim Auflisten der Versionen auftritt.
        """
        try:
            # Nur Verzeichnisse als Versionen betrachten
            versions = [d for d in os.listdir(self.versions_path) if os.path.isdir(os.path.join(self.versions_path, d))]
            versions.sort() # Für eine konsistente Reihenfolge
            logger.debug(f"Gefundene {len(versions)} Versionen für Agent '{os.path.basename(self.agent_path)}': {versions}")
            return versions
        except Exception as e:
            logger.error(f"Fehler beim Auflisten der Versionen für Agent '{os.path.basename(self.agent_path)}': {e}", exc_info=True)
            raise KnowledgeFlaskException(f"Fehler beim Auflisten der Versionen: {e}")

    def rollback_to_version(self, version_tag: str) -> bool:
        """
        Setzt die aktuelle Wissensbasis des Agenten auf eine spezifische Version zurück (Rollback).

        Args:
            version_tag (str): Der Tag der Version, zu der zurückgerollt werden soll.

        Returns:
            bool: True, wenn der Rollback erfolgreich war.

        Raises:
            KnowledgeFlaskException: Wenn die angegebene Version nicht gefunden wird
                                     oder ein Fehler während des Rollbacks auftritt.
        """
        source_version_path = os.path.join(self.versions_path, version_tag)
        if not os.path.exists(source_version_path) or not os.path.isdir(source_version_path):
            raise KnowledgeFlaskException(f"Version '{version_tag}' nicht gefunden unter {source_version_path}.")
        
        current_kb_path = self._get_current_kb_path()
        try:
            logger.warning(f"Führe Rollback für Agent '{os.path.basename(self.agent_path)}' auf Version '{version_tag}' durch.")
            logger.info(f"Sichere die aktuelle Wissensbasis vor dem Rollback...")

            # Schritt 1: Aktuelle Wissensbasis sichern
            if os.path.exists(current_kb_path):
                backup_path = f"{current_kb_path}_backup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                shutil.move(current_kb_path, backup_path)
                logger.info(f"Aktuelle Wissensbasis gesichert nach '{backup_path}'.")
            
            # Schritt 2: Versionierte Wissensbasis in den aktuellen KB-Pfad kopieren
            shutil.copytree(source_version_path, current_kb_path)
            
            logger.info(f"Agent '{os.path.basename(self.agent_path)}' erfolgreich auf Version '{version_tag}' zurückgerollt.")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Rollback des Agenten '{os.path.basename(self.agent_path)}' auf Version '{version_tag}': {e}", exc_info=True)
            raise KnowledgeFlaskException(f"Fehler bei der Versionierung (Rollback): {e}")

# --- CLI Command Handlers ---
def _validate_agent_name(agent_name: str) -> None:
    """Überprüft, ob der Agentenname gültig ist."""
    if not agent_name or not agent_name.isalnum():
        raise ValueError("Agentenname muss alphanumerisch sein und darf nicht leer sein.")

def create_agent_cmd(args: argparse.Namespace) -> None:
    """
    Behandelt den 'create'-Befehl: Erstellt einen neuen KnowledgeFlask-Agenten.
    """
    agent_name = args.name
    data_sources = args.data
    
    try:
        _validate_agent_name(agent_name)
        logger.info(f"Versuche, KnowledgeFlask-Agent '{agent_name}' zu erstellen...")

        kb_manager = KnowledgeBaseManager(agent_name)
        if kb_manager.create_from_data(data_sources, args.chunk_size, args.overlap):
            logger.info(f"Wissensbasis für Agent '{agent_name}' erfolgreich erstellt.")
            
            # Erstelle automatisch einen ersten Snapshot bei der Erstellung
            version_manager = VersionManager(agent_name)
            initial_tag = version_manager.create_snapshot("initial_creation")
            
            print(f"\n--- KnowledgeFlask ---")
            print(f"Agent '{agent_name}' erfolgreich erstellt von {len(data_sources)} Datenquellen.")
            print(f"Ein initialer Snapshot '{initial_tag}' wurde erstellt.")
            print(f"Sie können ihn jetzt abfragen: python main.py query {agent_name} \"Ihre Frage hier\"")
            print(f"----------------------")
            logger.info(f"Agent '{agent_name}' und initialer Snapshot erstellt.")
    except (KnowledgeFlaskException, ValueError) as e:
        logger.error(f"Fehler beim Erstellen des Agenten '{agent_name}': {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Ein unerwarteter Fehler ist während der Agentenerstellung aufgetreten: {e}", exc_info=True)
        sys.exit(1)

def query_agent_cmd(args: argparse.Namespace) -> None:
    """
    Behandelt den 'query'-Befehl: Fragt einen bestehenden KnowledgeFlask-Agenten ab.
    """
    agent_name = args.name
    question = args.question
    
    try:
        _validate_agent_name(agent_name)
        logger.info(f"Versuche, KnowledgeFlask-Agent '{agent_name}' abzufragen...")

        kb_manager = KnowledgeBaseManager(agent_name)
        agent = KnowledgeAgent(agent_name, kb_manager)
        agent.load() # Lädt die Wissensbasis und das LLM
        
        answer = agent.query(question, top_k=args.top_k)
        print(f"\n--- Antwort von '{agent_name}' ---")
        print(answer)
        print(f"----------------------------------")
        logger.info(f"Agent '{agent_name}' erfolgreich abgefragt.")
    except (KnowledgeFlaskException, ValueError) as e:
        logger.error(f"Fehler bei der Abfrage von Agent '{agent_name}': {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Ein unerwarteter Fehler ist während der Agentenabfrage aufgetreten: {e}", exc_info=True)
        sys.exit(1)

def list_agents_cmd(args: argparse.Namespace) -> None:
    """
    Behandelt den 'list'-Befehl: Listet alle verfügbaren KnowledgeFlask-Agenten auf.
    """
    if not os.path.exists(KF_AGENT_BASE_PATH):
        print("Keine KnowledgeFlask-Agenten gefunden.")
        return

    agents = [d for d in os.listdir(KF_AGENT_BASE_PATH) if os.path.isdir(os.path.join(KF_AGENT_BASE_PATH, d))]
    
    if not agents:
        print("Keine KnowledgeFlask-Agenten gefunden.")
        return
    
    print("\n--- Verfügbare KnowledgeFlask-Agenten ---")
    for agent_name in sorted(agents):
        print(f"- {agent_name}")
    print("------------------------------------------")
    logger.info(f"Liste der {len(agents)} Agenten angezeigt.")

def version_agent_cmd(args: argparse.Namespace) -> None:
    """
    Behandelt den 'version'-Befehl: Verwaltet Versionen für KnowledgeFlask-Agenten.
    """
    agent_name = args.name
    
    try:
        _validate_agent_name(agent_name)
        version_manager = VersionManager(agent_name)

        if args.action == 'list':
            versions = version_manager.list_versions()
            if versions:
                print(f"\n--- Versionen für Agent '{agent_name}' ---")
                for v in versions:
                    print(f"- {v}")
                print("------------------------------------------")
                logger.info(f"Versionen für Agent '{agent_name}' aufgelistet.")
            else:
                print(f"Keine Versionen für Agent '{agent_name}' gefunden.")
        elif args.action == 'snapshot':
            version_tag = args.tag
            tag = version_manager.create_snapshot(version_tag)
            print(f"\nSnapshot '{tag}' erfolgreich für Agent '{agent_name}' erstellt.")
            logger.info(f"Snapshot '{tag}' für Agent '{agent_name}' erstellt.")
        elif args.action == 'rollback':
            version_tag = args.tag
            if version_manager.rollback_to_version(version_tag):
                print(f"\nAgent '{agent_name}' erfolgreich auf Version '{version_tag}' zurückgerollt.")
                logger.info(f"Agent '{agent_name}' auf Version '{version_tag}' zurückgerollt.")
        else:
            raise ValueError(f"Unbekannte Versionierungsaktion: {args.action}")
    except (KnowledgeFlaskException, ValueError) as e:
        logger.error(f"Fehler bei der Versionierungsoperation für Agent '{agent_name}': {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Ein unerwarteter Fehler ist während der Versionierungsoperation aufgetreten: {e}", exc_info=True)
        sys.exit(1)

# --- Main CLI Entry Point ---
def main() -> None:
    """
    Haupt-Einstiegspunkt für die KnowledgeFlask-Befehlszeilenschnittstelle (CLI).
    Parsen von Argumenten und Weiterleitung an die entsprechenden Funktionen.
    """
    parser = argparse.ArgumentParser(
        prog="knowledgeflask",
        description="KnowledgeFlask: Open-Source Python-Toolkit zum Erstellen, Versionieren und Abfragen hochfokussierter KI-Wissensagenten.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Beispiele:
  knowledgeflask create my_agent -d data/documents/ manual.pdf
  knowledgeflask query my_agent "Was ist die empfohlene Wartungsintervall?"
  knowledgeflask list
  knowledgeflask version my_agent snapshot -t "Q1_update"
  knowledgeflask version my_agent list
  knowledgeflask version my_agent rollback snapshot_20231026100000
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Befehle", required=True)

    # Befehl: create
    create_parser = subparsers.add_parser(
        "create", 
        help="Erstellt einen neuen Wissensagenten aus Datenquellen.",
        description="""
        Erstellt einen neuen KnowledgeFlask-Agenten. 
        Dieser Befehl verarbeitet Ihre Daten, bettet sie ein und speichert sie als Wissensbasis.
        """
    )
    create_parser.add_argument(
        "name", 
        type=str, 
        help="Eindeutiger Name für den neuen Wissensagenten."
    )
    create_parser.add_argument(
        "-d", "--data", 
        nargs="+", 
        required=True,
        help="Einer oder mehrere Pfade zu Datendateien oder -verzeichnissen (z.B. 'data/docs/' 'data/report.pdf')."
    )
    create_parser.add_argument(
        "--chunk-size", 
        type=int, 
        default=500, 
        help="Größe der Text-Chunks für die Verarbeitung (Standard: 500 Zeichen)."
    )
    create_parser.add_argument(
        "--overlap", 
        type=int, 
        default=50, 
        help="Überlappung zwischen Text-Chunks (Standard: 50 Zeichen)."
    )
    create_parser.set_defaults(func=create_agent_cmd)

    # Befehl: query
    query_parser = subparsers.add_parser(
        "query", 
        help="Fragt einen bestehenden Wissensagenten ab.",
        description="""
        Fragt einen bestehenden KnowledgeFlask-Agenten mit einer natürlichsprachlichen Frage ab.
        Der Agent ruft relevante Informationen aus seiner Wissensbasis ab und liefert eine Antwort.
        """
    )
    query_parser.add_argument(
        "name", 
        type=str, 
        help="Name des abzufragenden Wissensagenten."
    )
    query_parser.add_argument(
        "question", 
        type=str, 
        help="Die Frage, die dem Wissensagenten gestellt werden soll."
    )
    query_parser.add_argument(
        "--top-k", 
        type=int, 
        default=3, 
        help="Anzahl der Top-relevanten Dokumente, die für die Beantwortung abgerufen werden sollen (Standard: 3)."
    )
    query_parser.set_defaults(func=query_agent_cmd)

    # Befehl: list
    list_parser = subparsers.add_parser(
        "list", 
        help="Listet alle erstellten Wissensagenten auf.",
        description="""
        Listet alle KnowledgeFlask-Agenten auf, die lokal erstellt wurden und verfügbar sind.
        """
    )
    list_parser.set_defaults(func=list_agents_cmd)

    # Befehl: version
    version_parser = subparsers.add_parser(
        "version", 
        help="Verwaltet Agentenversionen (Snapshot, Liste, Rollback).",
        description="""
        Verwaltet verschiedene Versionen der Wissensbasis eines KnowledgeFlask-Agenten.
        Sie können den aktuellen Zustand als Snapshot speichern, verfügbare Snapshots auflisten
        oder zu einem früheren Zustand zurückrollen.
        """
    )
    version_parser.add_argument(
        "name", 
        type=str, 
        help="Name des Wissensagenten, dessen Versionen verwaltet werden sollen."
    )
    version_subparsers = version_parser.add_subparsers(
        dest="action", 
        required=True, 
        help="Aktionen zur Versionierung"
    )

    # Versionierungsaktion: list
    version_list_parser = version_subparsers.add_parser(
        "list", 
        help="Listet alle Versionen für den angegebenen Agenten auf."
    )
    version_list_parser.set_defaults(func=version_agent_cmd)

    # Versionierungsaktion: snapshot
    version_snapshot_parser = version_subparsers.add_parser(
        "snapshot", 
        help="Erstellt einen versionierten Snapshot der aktuellen Wissensbasis des Agenten."
    )
    version_snapshot_parser.add_argument(
        "-t", "--tag", 
        type=str, 
        default=None, 
        help="Optional: Ein benutzerdefinierter Tag für den Snapshot (z.B. 'pre_Q4_update'). Wenn nicht angegeben, wird ein zeitgestempelter Tag generiert."
    )
    version_snapshot_parser.set_defaults(func=version_agent_cmd)

    # Versionierungsaktion: rollback
    version_rollback_parser = version_subparsers.add_parser(
        "rollback", 
        help="Setzt die aktuelle Wissensbasis des Agenten auf eine bestimmte Version zurück."
    )
    version_rollback_parser.add_argument(
        "tag", 
        type=str, 
        help="Der Versionstag, zu dem zurückgerollt werden soll."
    )
    version_rollback_parser.set_defaults(func=version_agent_cmd)

    # Argumente parsen und die entsprechende Funktion ausführen
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
