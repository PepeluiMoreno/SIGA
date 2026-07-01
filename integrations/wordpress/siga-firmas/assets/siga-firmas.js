/* global SIGAFirmas */
( function () {
	'use strict';

	var cfg = window.SIGAFirmas || {};
	var widgets = []; // { form, el, id, getToken }

	/**
	 * Renderiza el widget de captcha en un contenedor, según el proveedor.
	 * Devuelve una función que lee el token actual, o null si no hay captcha.
	 */
	function renderCaptcha( el ) {
		if ( ! el || ! cfg.captchaSiteKey ) {
			return null;
		}
		var sitekey = el.getAttribute( 'data-sitekey' ) || cfg.captchaSiteKey;

		if ( cfg.captchaProvider === 'turnstile' && window.turnstile ) {
			var tId = window.turnstile.render( el, { sitekey: sitekey } );
			return function () {
				return window.turnstile.getResponse( tId );
			};
		}
		if ( cfg.captchaProvider === 'hcaptcha' && window.hcaptcha ) {
			var hId = window.hcaptcha.render( el, { sitekey: sitekey } );
			return function () {
				return window.hcaptcha.getResponse( hId );
			};
		}
		return null;
	}

	/** Espera a que la API del captcha esté disponible y entonces renderiza. */
	function setupCaptchas() {
		var pending = false;

		document.querySelectorAll( '.siga-firmas-form' ).forEach( function ( form ) {
			var el = form.querySelector( '.siga-firmas-captcha' );
			if ( ! el ) {
				return;
			}
			var getToken = renderCaptcha( el );
			if ( getToken ) {
				widgets.push( { form: form, getToken: getToken } );
			} else if ( cfg.captchaSiteKey && cfg.captchaProvider !== 'none' ) {
				pending = true; // La API aún no ha cargado; reintentamos.
			}
		} );

		if ( pending ) {
			setTimeout( setupCaptchas, 300 );
		}
	}

	/** Token del captcha asociado a un formulario (o '' si no aplica). */
	function tokenFor( form ) {
		for ( var i = 0; i < widgets.length; i++ ) {
			if ( widgets[ i ].form === form ) {
				try {
					return widgets[ i ].getToken() || '';
				} catch ( e ) {
					return '';
				}
			}
		}
		return '';
	}

	// Validación de NIF español (DNI/NIE) con letra de control.
	var NIF_LETRAS = 'TRWAGMYFPDXBNJZSQVHLCKE';
	function normalizarNif( v ) {
		return ( v || '' ).replace( /[\s\-.]/g, '' ).toUpperCase();
	}
	function validarNif( v ) {
		var n = normalizarNif( v );
		var dni = /^(\d{8})([A-Z])$/.exec( n );
		if ( dni ) {
			return NIF_LETRAS.charAt( parseInt( dni[ 1 ], 10 ) % 23 ) === dni[ 2 ];
		}
		var nie = /^([XYZ])(\d{7})([A-Z])$/.exec( n );
		if ( nie ) {
			var base = ( { X: '0', Y: '1', Z: '2' } )[ nie[ 1 ] ] + nie[ 2 ];
			return NIF_LETRAS.charAt( parseInt( base, 10 ) % 23 ) === nie[ 3 ];
		}
		return false;
	}

	function setMsg( form, text, kind ) {
		var msg = form.querySelector( '.siga-firmas-msg' );
		if ( ! msg ) {
			return;
		}
		msg.textContent = text || '';
		msg.className = 'siga-firmas-msg' + ( kind ? ' is-' + kind : '' );
	}

	function onSubmit( e ) {
		e.preventDefault();
		var form = e.currentTarget;
		var btn = form.querySelector( '.siga-firmas-submit' );

		if ( ! form.checkValidity() ) {
			form.reportValidity();
			return;
		}

		// NIF: obligatorio y bien formado, salvo extranjero sin NIF (casilla).
		var sinNif = form.querySelector( '[data-siga-sin-nif]' );
		var esExtranjero = !!( sinNif && sinNif.checked );
		var nifInput = form.querySelector( '[data-siga-nif]' );
		var nif = normalizarNif( nifInput ? nifInput.value : '' );
		if ( ! esExtranjero ) {
			if ( ! validarNif( nif ) ) {
				setMsg( form, cfg.i18n.nifInvalido, 'error' );
				if ( nifInput ) { nifInput.focus(); }
				return;
			}
			if ( nifInput ) { nifInput.value = nif; }  // dejar el valor normalizado a la vista
		} else {
			nif = '';  // extranjero sin NIF: dedup blanda por nombre en el backend
		}

		var needsCaptcha = cfg.captchaProvider && cfg.captchaProvider !== 'none' && cfg.captchaSiteKey;
		var captchaToken = tokenFor( form );
		if ( needsCaptcha && ! captchaToken ) {
			setMsg( form, cfg.i18n.captchaFalta, 'error' );
			return;
		}

		var data = new FormData( form );
		var payload = {
			actividad_id: form.getAttribute( 'data-actividad' ) || '',
			nombre: data.get( 'nombre' ) || '',
			apellidos: data.get( 'apellidos' ) || '',
			email: data.get( 'email' ) || '',
			codigo_postal: data.get( 'codigo_postal' ) || '',
			documento: nif,
			tipo_documento: data.get( 'tipo_documento' ) || '',
			acepta_terminos: data.get( 'acepta_terminos' ) ? '1' : '',
			acepta_comunicaciones: data.get( 'acepta_comunicaciones' ) ? '1' : '',
			website: data.get( 'website' ) || '',
			captcha_token: captchaToken
		};

		btn.disabled = true;
		var btnLabel = btn.textContent;
		btn.textContent = cfg.i18n.enviando;
		setMsg( form, '', '' );

		fetch( cfg.restUrl, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-WP-Nonce': cfg.nonce
			},
			body: JSON.stringify( payload )
		} )
			.then( function ( res ) {
				return res.json().then( function ( body ) {
					return { ok: res.ok, body: body };
				} );
			} )
			.then( function ( r ) {
				if ( r.ok && r.body && r.body.ok ) {
					setMsg( form, r.body.mensaje || '', 'ok' );
					form.reset();
				} else {
					setMsg( form, ( r.body && r.body.mensaje ) || cfg.i18n.errorGenerico, 'error' );
				}
			} )
			.catch( function () {
				setMsg( form, cfg.i18n.errorGenerico, 'error' );
			} )
			.finally( function () {
				btn.disabled = false;
				btn.textContent = btnLabel;
			} );
	}

	function init() {
		document.querySelectorAll( '.siga-firmas-form' ).forEach( function ( form ) {
			form.addEventListener( 'submit', onSubmit );

			// Casilla "extranjero sin NIF": libera el DNI/NIE de obligatorio.
			var sinNif = form.querySelector( '[data-siga-sin-nif]' );
			var nifInput = form.querySelector( '[data-siga-nif]' );
			var req = form.querySelector( '.siga-firmas-nif-req' );
			if ( sinNif && nifInput ) {
				sinNif.addEventListener( 'change', function () {
					nifInput.required = ! sinNif.checked;
					nifInput.disabled = sinNif.checked;
					if ( req ) { req.style.display = sinNif.checked ? 'none' : ''; }
				} );
			}
		} );
		setupCaptchas();
	}

	if ( document.readyState === 'loading' ) {
		document.addEventListener( 'DOMContentLoaded', init );
	} else {
		init();
	}
} )();
