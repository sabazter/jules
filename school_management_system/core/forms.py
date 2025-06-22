from django import forms
from django.utils.translation import gettext_lazy as _
from .models import GradeLevel # Will be uncommented/used when GradeLevel is confirmed in models

class PreEnrollmentForm(forms.Form):
    # Datos del Alumno
    foto_alumno = forms.ImageField(label=_("Foto del Alumno"), required=False)
    nombres_alumno = forms.CharField(label=_("Nombres del Alumno"), max_length=100)
    apellidos_alumno = forms.CharField(label=_("Apellidos del Alumno"), max_length=100)
    cedula_alumno = forms.CharField(label=_("Número de Cédula del Alumno"), max_length=20, help_text=_("Ej: V12345678 o E12345678"))
    pais_nacimiento_alumno = forms.CharField(label=_("País de Nacimiento"), max_length=100)
    estado_nacimiento_alumno = forms.CharField(label=_("Estado/Provincia de Nacimiento"), max_length=100)
    municipio_nacimiento_alumno = forms.CharField(label=_("Municipio/Ciudad de Nacimiento"), max_length=100)
    lugar_residencia_actual_alumno = forms.CharField(label=_("Dirección de Residencia Actual"), widget=forms.Textarea(attrs={'rows': 3}))
    edad_alumno = forms.IntegerField(label=_("Edad (años cumplidos)"))
    correo_electronico_alumno = forms.EmailField(label=_("Correo Electrónico del Alumno"))

    # grado_aspirado = forms.ModelChoiceField(
    #     queryset=GradeLevel.objects.all(), # This will be adjusted based on available GradeLevel instances
    #     label=_("Grado/Año al que Aspira"),
    #     empty_label=_("Seleccione..."),
    #     help_text=_("Seleccione el grado o año al que el alumno desea ingresar.")
    # )
    # Temporary field until GradeLevel is finalized and populated
    grado_aspirado_temp = forms.ChoiceField(
        label=_("Grado/Año al que Aspira"),
        choices=[
            ('', _('Seleccione...')),
            ('prekinder', _('Prekinder')), ('kinder', _('Kinder')), ('preparatorio', _('Preparatorio')),
            ('1g', _('1er Grado')), ('2g', _('2do Grado')), ('3g', _('3er Grado')),
            ('4g', _('4to Grado')), ('5g', _('5to Grado')), ('6g', _('6to Grado')),
            ('1a', _('1er Año')), ('2a', _('2do Año')), ('3a', _('3er Año')),
            ('4a', _('4to Año')), ('5a', _('5to Año')),
        ],
        required=True,
        help_text=_("Seleccione el grado o año al que el alumno desea ingresar.")
    )

    # Datos de la Madre
    nombres_madre = forms.CharField(label=_("Nombres Completos (Madre)"), max_length=100, required=False)
    apellidos_madre = forms.CharField(label=_("Apellidos Completos (Madre)"), max_length=100, required=False)
    cedula_madre = forms.CharField(label=_("Cédula de Identidad (Madre)"), max_length=20, required=False, help_text=_("Ej: V12345678"))
    pais_nacimiento_madre = forms.CharField(label=_("País de Nacimiento (Madre)"), max_length=100, required=False)
    estado_nacimiento_madre = forms.CharField(label=_("Estado/Provincia de Nacimiento (Madre)"), max_length=100, required=False)
    municipio_nacimiento_madre = forms.CharField(label=_("Municipio/Ciudad de Nacimiento (Madre)"), max_length=100, required=False)
    lugar_residencia_actual_madre = forms.CharField(label=_("Dirección de Residencia Actual (Madre)"), widget=forms.Textarea(attrs={'rows': 3}), required=False)
    edad_madre = forms.IntegerField(label=_("Edad (Madre)"), required=False)
    correo_electronico_madre = forms.EmailField(label=_("Correo Electrónico (Madre)"), required=False)
    rif_madre = forms.CharField(label=_("RIF (Madre)"), max_length=20, required=False, help_text=_("Ej: V123456789"))
    profesion_madre = forms.CharField(label=_("Profesión (Madre)"), max_length=100, required=False)
    lugar_trabajo_madre = forms.CharField(label=_("Lugar de Trabajo (Madre)"), max_length=100, required=False)
    telefono_habitacion_madre = forms.CharField(label=_("Teléfono de Habitación (Madre)"), max_length=20, required=False)
    telefono_movil_madre = forms.CharField(label=_("Teléfono Móvil (Madre)"), max_length=20, required=False)
    madre_fallecida = forms.BooleanField(label=_("Madre Fallecida"), required=False, help_text=_("Marque esta casilla si la madre ha fallecido."))

    # Datos del Padre
    nombres_padre = forms.CharField(label=_("Nombres Completos (Padre)"), max_length=100, required=False)
    apellidos_padre = forms.CharField(label=_("Apellidos Completos (Padre)"), max_length=100, required=False)
    cedula_padre = forms.CharField(label=_("Cédula de Identidad (Padre)"), max_length=20, required=False, help_text=_("Ej: V12345678"))
    pais_nacimiento_padre = forms.CharField(label=_("País de Nacimiento (Padre)"), max_length=100, required=False)
    estado_nacimiento_padre = forms.CharField(label=_("Estado/Provincia de Nacimiento (Padre)"), max_length=100, required=False)
    municipio_nacimiento_padre = forms.CharField(label=_("Municipio/Ciudad de Nacimiento (Padre)"), max_length=100, required=False)
    lugar_residencia_actual_padre = forms.CharField(label=_("Dirección de Residencia Actual (Padre)"), widget=forms.Textarea(attrs={'rows': 3}), required=False)
    edad_padre = forms.IntegerField(label=_("Edad (Padre)"), required=False)
    correo_electronico_padre = forms.EmailField(label=_("Correo Electrónico (Padre)"), required=False)
    rif_padre = forms.CharField(label=_("RIF (Padre)"), max_length=20, required=False, help_text=_("Ej: V123456789"))
    profesion_padre = forms.CharField(label=_("Profesión (Padre)"), max_length=100, required=False)
    lugar_trabajo_padre = forms.CharField(label=_("Lugar de Trabajo (Padre)"), max_length=100, required=False)
    telefono_habitacion_padre = forms.CharField(label=_("Teléfono de Habitación (Padre)"), max_length=20, required=False)
    telefono_movil_padre = forms.CharField(label=_("Teléfono Móvil (Padre)"), max_length=20, required=False)
    padre_fallecido = forms.BooleanField(label=_("Padre Fallecido"), required=False, help_text=_("Marque esta casilla si el padre ha fallecido."))

    # Datos Médicos del Alumno
    peso_alumno = forms.FloatField(label=_("Peso del Alumno (kg)"), required=False, help_text=_("Ej: 30.5"))
    altura_alumno = forms.FloatField(label=_("Altura del Alumno (cm)"), required=False, help_text=_("Ej: 120.0"))
    talla_pantalon_alumno = forms.CharField(label=_("Talla de Pantalón"), max_length=10, required=False)
    talla_camisa_alumno = forms.CharField(label=_("Talla de Camisa"), max_length=10, required=False)
    talla_zapatos_alumno = forms.CharField(label=_("Talla de Zapatos"), max_length=10, required=False)

    VACUNA_CHOICES = [
        ('bcg', _('BCG (Tuberculosis)')), ('hepatitis_b_rn', _('Hepatitis B (Recién Nacido)')),
        ('pentavalente_1', _('Pentavalente (1ra Dosis - Difteria, Tétanos, Tos Ferina, Haemophilus Influenzae tipo B, Hepatitis B)')),
        ('polio_1', _('Polio Inyectable (1ra Dosis)')),
        ('rotavirus_1', _('Rotavirus (1ra Dosis)')), ('neumococo_1', _('Neumococo Conjugada (1ra Dosis)')),
        ('pentavalente_2', _('Pentavalente (2da Dosis)')), ('polio_2', _('Polio Inyectable (2da Dosis)')),
        ('rotavirus_2', _('Rotavirus (2da Dosis)')), ('neumococo_2', _('Neumococo Conjugada (2da Dosis)')),
        ('pentavalente_3', _('Pentavalente (3ra Dosis)')), ('polio_3', _('Polio Oral (3ra Dosis)')),
        ('srp_1', _('SRP (Sarampión, Rubéola, Parotiditis - 1ra Dosis)')), ('fiebre_amarilla', _('Fiebre Amarilla')),
        ('influenza_1', _('Influenza (1ra Dosis Anual)')), ('influenza_2', _('Influenza (2da Dosis Anual, si aplica)')),
        ('srp_refuerzo', _('SRP Refuerzo')), ('polio_refuerzo_1', _('Polio Oral (1er Refuerzo)')),
        ('dpt_refuerzo_1', _('DPT (Difteria, Tétanos, Tos Ferina - 1er Refuerzo)')),
        ('polio_refuerzo_2', _('Polio Oral (2do Refuerzo)')),
        ('dpt_refuerzo_2', _('DPT (2do Refuerzo)')),
        ('toxoide_tetanico', _('Toxoide Tetánico Diftérico (Td cada 10 años)')),
        ('vph', _('VPH (Virus del Papiloma Humano, si aplica según edad)')),
        ('otra', _('Otra(s) - Especificar abajo')),
    ]
    vacunas_recibidas = forms.MultipleChoiceField(
        label=_("Vacunas Recibidas (Marque todas las que apliquen)"), choices=VACUNA_CHOICES,
        widget=forms.CheckboxSelectMultiple, required=False
    )
    otras_vacunas_especificar = forms.CharField(label=_("Otras Vacunas (Especifique cuáles y fechas si es posible)"), max_length=255, required=False, widget=forms.Textarea(attrs={'rows': 2}))
    condiciones_medicas_relevantes = forms.CharField(label=_("Condiciones Médicas Relevantes (Enfermedades crónicas, etc.)"), widget=forms.Textarea(attrs={'rows': 3}), required=False)
    alergias_conocidas = forms.CharField(label=_("Alergias Conocidas (Medicamentos, alimentos, etc.)"), widget=forms.Textarea(attrs={'rows': 3}), required=False)
    medicamentos_regulares = forms.CharField(label=_("Medicamentos que Toma Regularmente (Dosis y frecuencia)"), widget=forms.Textarea(attrs={'rows': 3}), required=False)
    seguro_medico = forms.CharField(label=_("Seguro Médico (Nombre de la compañía y número de póliza)"), max_length=150, required=False)

    # Datos de Vehículos (Permitir agregar hasta 2 vehículos inicialmente)
    # Vehículo 1
    tipo_vehiculo_1 = forms.CharField(label=_("Tipo de Vehículo 1 (Ej: Carro, Moto)"), max_length=50, required=False)
    marca_vehiculo_1 = forms.CharField(label=_("Marca Vehículo 1"), max_length=50, required=False)
    modelo_vehiculo_1 = forms.CharField(label=_("Modelo Vehículo 1"), max_length=50, required=False)
    placa_vehiculo_1 = forms.CharField(label=_("Placa Vehículo 1"), max_length=20, required=False)
    color_vehiculo_1 = forms.CharField(label=_("Color Vehículo 1"), max_length=30, required=False)

    # Vehículo 2
    tipo_vehiculo_2 = forms.CharField(label=_("Tipo de Vehículo 2"), max_length=50, required=False)
    marca_vehiculo_2 = forms.CharField(label=_("Marca Vehículo 2"), max_length=50, required=False)
    modelo_vehiculo_2 = forms.CharField(label=_("Modelo Vehículo 2"), max_length=50, required=False)
    placa_vehiculo_2 = forms.CharField(label=_("Placa Vehículo 2"), max_length=20, required=False)
    color_vehiculo_2 = forms.CharField(label=_("Color Vehículo 2"), max_length=30, required=False)

    # Representante Legal
    REPRESENTANTE_LEGAL_CHOICES = [
        ('', _('Seleccione...')),
        ('madre', _('Madre (Datos ya proporcionados)')),
        ('padre', _('Padre (Datos ya proporcionados)')),
        ('otro', _('Otro (Especificar abajo)')),
    ]
    quien_es_representante_legal = forms.ChoiceField(
        label=_("¿Quién es el Representante Legal del Alumno?"),
        choices=REPRESENTANTE_LEGAL_CHOICES,
        required=True,
        widget=forms.RadioSelect, # Radio buttons might be better here
        help_text=_("Seleccione quién actuará como representante legal.")
    )
    # Campos para 'Otro' Representante Legal (se mostrarán condicionalmente con JS)
    nombres_representante_legal_otro = forms.CharField(label=_("Nombres Completos (Rep. Legal Otro)"), max_length=100, required=False)
    apellidos_representante_legal_otro = forms.CharField(label=_("Apellidos Completos (Rep. Legal Otro)"), max_length=100, required=False)
    cedula_representante_legal_otro = forms.CharField(label=_("Cédula (Rep. Legal Otro)"), max_length=20, required=False)
    pais_nacimiento_rl_otro = forms.CharField(label=_("País Nacimiento (Rep. Legal Otro)"), max_length=100, required=False)
    estado_nacimiento_rl_otro = forms.CharField(label=_("Estado Nacimiento (Rep. Legal Otro)"), max_length=100, required=False)
    municipio_nacimiento_rl_otro = forms.CharField(label=_("Municipio Nacimiento (Rep. Legal Otro)"), max_length=100, required=False)
    lugar_residencia_actual_rl_otro = forms.CharField(label=_("Residencia Actual (Rep. Legal Otro)"), widget=forms.Textarea(attrs={'rows':3}), required=False)
    edad_rl_otro = forms.IntegerField(label=_("Edad (Rep. Legal Otro)"), required=False)
    correo_electronico_rl_otro = forms.EmailField(label=_("Correo (Rep. Legal Otro)"), required=False)
    telefono_rl_otro = forms.CharField(label=_("Teléfono (Rep. Legal Otro)"), max_length=20, required=False)
    parentesco_rl_otro = forms.CharField(label=_("Parentesco con el Alumno (Rep. Legal Otro)"), max_length=50, required=False)


    # Persona Responsable del Pago
    RESPONSABLE_PAGO_CHOICES = [
        ('', _('Seleccione...')),
        ('madre', _('Madre (Datos ya proporcionados)')),
        ('padre', _('Padre (Datos ya proporcionados)')),
        ('representante_legal_seleccionado', _("Mismo Representante Legal (si es 'Otro')")),
        ('otra_persona_pago', _('Otra Persona (Especificar abajo)')),
    ]
    quien_es_responsable_pago = forms.ChoiceField(
        label=_("¿Quién es la Persona Responsable del Pago de las Mensualidades?"),
        choices=RESPONSABLE_PAGO_CHOICES,
        required=True,
        widget=forms.RadioSelect,
        help_text=_("Seleccione quién se hará cargo de los pagos.")
    )
    # Campos para 'Otra Persona' Responsable del Pago (se mostrarán condicionalmente con JS)
    nombres_responsable_pago_otro = forms.CharField(label=_("Nombres Completos (Resp. Pago Otro)"), max_length=100, required=False)
    apellidos_responsable_pago_otro = forms.CharField(label=_("Apellidos Completos (Resp. Pago Otro)"), max_length=100, required=False)
    cedula_responsable_pago_otro = forms.CharField(label=_("Cédula (Resp. Pago Otro)"), max_length=20, required=False)
    rif_responsable_pago_otro = forms.CharField(label=_("RIF (Resp. Pago Otro)"), max_length=20, required=False)
    pais_nacimiento_rp_otro = forms.CharField(label=_("País Nacimiento (Resp. Pago Otro)"), max_length=100, required=False)
    estado_nacimiento_rp_otro = forms.CharField(label=_("Estado Nacimiento (Resp. Pago Otro)"), max_length=100, required=False)
    municipio_nacimiento_rp_otro = forms.CharField(label=_("Municipio Nacimiento (Resp. Pago Otro)"), max_length=100, required=False)
    lugar_residencia_actual_rp_otro = forms.CharField(label=_("Residencia (Resp. Pago Otro)"), widget=forms.Textarea(attrs={'rows':3}), required=False)
    edad_rp_otro = forms.IntegerField(label=_("Edad (Resp. Pago Otro)"), required=False)
    correo_electronico_rp_otro = forms.EmailField(label=_("Correo (Resp. Pago Otro)"), required=False)
    telefono_rp_otro = forms.CharField(label=_("Teléfono (Resp. Pago Otro)"), max_length=20, required=False)
    parentesco_rp_otro = forms.CharField(label=_("Parentesco con el Alumno (Resp. Pago Otro)"), max_length=50, required=False)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make 'otro' fields for legal representative not required by default
        # They will be made required by JavaScript if 'otro' is selected.
        # Same for 'otra_persona_pago' fields.

        # Helper to make fields not required
        fields_to_make_not_required_rl = [
            'nombres_representante_legal_otro', 'apellidos_representante_legal_otro',
            'cedula_representante_legal_otro', 'pais_nacimiento_rl_otro',
            'estado_nacimiento_rl_otro', 'municipio_nacimiento_rl_otro',
            'lugar_residencia_actual_rl_otro', 'edad_rl_otro',
            'correo_electronico_rl_otro', 'telefono_rl_otro', 'parentesco_rl_otro',
        ]
        for field_name in fields_to_make_not_required_rl:
            if field_name in self.fields:
                self.fields[field_name].required = False

        fields_to_make_not_required_rp = [
            'nombres_responsable_pago_otro', 'apellidos_responsable_pago_otro',
            'cedula_responsable_pago_otro', 'rif_responsable_pago_otro',
            'pais_nacimiento_rp_otro', 'estado_nacimiento_rp_otro',
            'municipio_nacimiento_rp_otro', 'lugar_residencia_actual_rp_otro',
            'edad_rp_otro', 'correo_electronico_rp_otro', 'telefono_rp_otro',
            'parentesco_rp_otro',
        ]
        for field_name in fields_to_make_not_required_rp:
            if field_name in self.fields:
                self.fields[field_name].required = False

        # Conditional logic for 'Otro' fields will be primarily handled by JavaScript on the frontend
        # for a better user experience. Backend validation will ensure data integrity.

    def clean(self):
        cleaned_data = super().clean()

        # Conditional validation for 'Otro' Representante Legal
        quien_es_rl = cleaned_data.get('quien_es_representante_legal')
        if quien_es_rl == 'otro':
            required_fields_rl_otro = {
                'nombres_representante_legal_otro': _("Nombres (Representante Legal)"),
                'apellidos_representante_legal_otro': _("Apellidos (Representante Legal)"),
                'cedula_representante_legal_otro': _("Cédula (Representante Legal)"),
                'lugar_residencia_actual_rl_otro': _("Residencia Actual (Representante Legal)"),
                'telefono_rl_otro': _("Teléfono (Representante Legal)"),
                'parentesco_rl_otro': _("Parentesco con el Alumno (Representante Legal)")
            }
            for field_name, field_label in required_fields_rl_otro.items():
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, forms.ValidationError(_("Este campo es obligatorio cuando se selecciona 'Otro' representante legal."), code='required'))

        # Conditional validation for 'Otra Persona' Responsable del Pago
        quien_es_rp = cleaned_data.get('quien_es_responsable_pago')
        if quien_es_rp == 'otra_persona_pago':
            required_fields_rp_otro = {
                'nombres_responsable_pago_otro': _("Nombres (Responsable Pago)"),
                'apellidos_responsable_pago_otro': _("Apellidos (Responsable Pago)"),
                'cedula_responsable_pago_otro': _("Cédula (Responsable Pago)"),
                'rif_responsable_pago_otro': _("RIF (Responsable Pago)"),
                'lugar_residencia_actual_rp_otro': _("Residencia Actual (Responsable Pago)"),
                'telefono_rp_otro': _("Teléfono (Responsable Pago)")
            }
            for field_name, field_label in required_fields_rp_otro.items():
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, forms.ValidationError(_("Este campo es obligatorio cuando se selecciona 'Otra Persona' para el pago."), code='required'))

        # At least one parent (Mother or Father) should have data unless both are marked as deceased.
        madre_fallecida = cleaned_data.get('madre_fallecida', False)
        padre_fallecido = cleaned_data.get('padre_fallecido', False)

        if not madre_fallecida and not padre_fallecido:
            # Check if at least one parent has some identifiable information
            madre_has_info = any(cleaned_data.get(f) for f in ['nombres_madre', 'apellidos_madre', 'cedula_madre'])
            padre_has_info = any(cleaned_data.get(f) for f in ['nombres_padre', 'apellidos_padre', 'cedula_padre'])
            if not madre_has_info and not padre_has_info:
                 self.add_error(None, forms.ValidationError(
                     _("Debe proporcionar información de al menos uno de los padres (madre o padre), o marcar ambos como fallecidos."),
                     code='no_parent_info'
                 ))
            elif not madre_fallecida and not madre_has_info and cleaned_data.get('quien_es_representante_legal') == 'madre':
                 self.add_error('quien_es_representante_legal', forms.ValidationError(
                     _("Si la madre es representante legal, debe proporcionar sus datos."), code='madre_rl_no_data'
                 ))
            elif not padre_fallecido and not padre_has_info and cleaned_data.get('quien_es_representante_legal') == 'padre':
                self.add_error('quien_es_representante_legal', forms.ValidationError(
                     _("Si el padre es representante legal, debe proporcionar sus datos."), code='padre_rl_no_data'
                 ))
            # Similar checks for responsable_pago
            if not madre_fallecida and not madre_has_info and cleaned_data.get('quien_es_responsable_pago') == 'madre':
                 self.add_error('quien_es_responsable_pago', forms.ValidationError(
                     _("Si la madre es responsable de pago, debe proporcionar sus datos."), code='madre_rp_no_data'
                 ))
            elif not padre_fallecido and not padre_has_info and cleaned_data.get('quien_es_responsable_pago') == 'padre':
                self.add_error('quien_es_responsable_pago', forms.ValidationError(
                     _("Si el padre es responsable de pago, debe proporcionar sus datos."), code='padre_rp_no_data'
                 ))


        # If 'Mismo Representante Legal (si es Otro)' is chosen for payment,
        # and 'Otro' was chosen for legal representative, copy data or ensure 'Otro RL' is filled.
        if quien_es_rp == 'representante_legal_seleccionado' and quien_es_rl != 'otro':
            self.add_error('quien_es_responsable_pago', forms.ValidationError(
                _("Esta opción es válida solo si el Representante Legal es 'Otro' y sus datos han sido llenados."),
                code='rp_rl_otro_mismatch'
            ))
        elif quien_es_rp == 'representante_legal_seleccionado' and quien_es_rl == 'otro':
            # Ensure that 'Otro RL' fields are filled if this option is chosen.
            # The individual field checks for 'Otro RL' above should handle this.
            # If 'Otro RL' fields are empty, this option is invalid.
            if not all(cleaned_data.get(f) for f in ['nombres_representante_legal_otro', 'cedula_representante_legal_otro']):
                 self.add_error('quien_es_responsable_pago', forms.ValidationError(
                    _("Los datos del 'Otro Representante Legal' deben estar completos para seleccionarlo como responsable de pago."),
                    code='rp_rl_otro_incomplete'
                ))


        return cleaned_data

from .models import ChatMessage # Import ChatMessage model

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Escribe tu mensaje...')})
        }
        labels = {
            'content': _('Mensaje')
        }
