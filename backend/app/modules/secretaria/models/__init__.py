"""Modelos del módulo de Secretaría."""

from .reunion import (
    TipoReunion,
    Reunion,
    AsistenteReunionSecretaria,
    PuntoOrdenDia,
    Acuerdo,
    VotacionAcuerdo,
)
from .acta import Acta, CertificadoAcuerdo
from .libro_socios import LibroSociosSnapshot
from .convenio import TipoConvenio, Convenio, ConvenioInstitucional, DelegacionFirma
from .plataforma_telematica import PlataformaTelematica

__all__ = [
    "TipoReunion", "Reunion", "AsistenteReunionSecretaria",
    "PuntoOrdenDia", "Acuerdo", "VotacionAcuerdo",
    "Acta", "CertificadoAcuerdo",
    "LibroSociosSnapshot",
    "TipoConvenio", "Convenio", "ConvenioInstitucional", "DelegacionFirma",
    "PlataformaTelematica",
]
