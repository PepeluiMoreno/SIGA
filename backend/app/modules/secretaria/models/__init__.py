"""Modelos del módulo de Secretaría."""

from .reunion import (
    TipoReunion,
    Reunion,
    AsistenteReunion,
    PuntoOrdenDia,
    Acuerdo,
    VotacionAcuerdo,
)
from .acta import Acta, CertificadoAcuerdo
from .libro_socios import LibroSociosSnapshot
from .convenio import TipoConvenio, Convenio, DelegacionFirma

__all__ = [
    "TipoReunion", "Reunion", "AsistenteReunion",
    "PuntoOrdenDia", "Acuerdo", "VotacionAcuerdo",
    "Acta", "CertificadoAcuerdo",
    "LibroSociosSnapshot",
    "TipoConvenio", "Convenio", "DelegacionFirma",
]
