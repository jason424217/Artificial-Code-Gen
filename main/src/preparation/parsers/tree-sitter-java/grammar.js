const DIGITS = token(sep1(/[0-9]+/, /_+/))
const HEX_DIGITS = token(sep1(/[A-Fa-f0-9]+/, '_'))
const PREC = {
  COMMA: -1,
  DECLARATION: 1,
  COMMENT: 1,
  ASSIGN: 0,
  OBJECT: 1,
  TERNARY: 1,
  OR: 2,
  AND: 3,
  PLUS: 4,
  REL: 5,
  TIMES: 6,
  TYPEOF: 7,
  DELETE: 7,
  VOID: 7,
  NOT: 8,
  NEG: 9,
  INC: 10,
  NEW: 11,
  CALL: 12,
  MEMBER: 13,
  CAST: 15,
};

module.exports = grammar({
  name: 'java',

  extras: $ => [
    $.comment,
    /\s/
  ],

  supertypes: $ => [
    $._expression,
    $._declaration,
    $._statement,
    $._literal,
    $._primary,
    $._type,
    $._simple_type,
    $._unannotated_type,
  ],

  inline: $ => [
    $._numeric_type,
    $._ambiguous_name,
    $._simple_type,
    $._reserved_identifier,
    $._class_member_declaration,
    $._interface_member_declaration,
    $._annotation_type_member_declaration,
    $._class_body_declaration,
    $._variable_initializer
  ],

  conflicts: $ => [
    [$.modifiers, $.annotated_type, $.receiver_parameter],
    [$.modifiers, $.annotated_type, $.module_declaration, $.package_declaration],
    [$._variable_declarator_id],
    [$._unannotated_type, $._expression],
    [$._unannotated_type, $._expression, $.inferred_parameters],
    [$._unannotated_type, $.class_literal],
    [$._unannotated_type, $.class_literal, $.array_access],
    [$._unannotated_type, $.method_reference],
    [$._unannotated_type, $.generic_type],
    [$._expression, $.generic_type],
    [$.scoped_identifier, $.scoped_type_identifier],
  ],

  word: $ => $.identifier,

  rules: {
    program: $ => repeat($._statement),

    // Literals

    _literal: $ => choice(
      $.decimal_integer_literal,
      $.hex_integer_literal,
      $.octal_integer_literal,
      $.binary_integer_literal,
      $.decimal_floating_point_literal,
      $.hex_floating_point_literal,
      $.true,
      $.false,
      $.character_literal,
      $.string_literal,
      $.null_literal
    ),

    decimal_integer_literal: $ => token(seq(
      DIGITS,
      optional(choice('l', 'L'))
    )),

    hex_integer_literal: $ => token(seq(
      choice('0x', '0X'),
      HEX_DIGITS,
      optional(choice('l', 'L'))
    )),

    octal_integer_literal: $ => token(seq(
      choice('0o', '0O'),
      sep1(/[0-7]+/, '_'),
      optional(choice('l', 'L'))
    )),

    binary_integer_literal: $ => token(seq(
      choice('0b', '0B'),
      sep1(/[01]+/, '_'),
      optional(choice('l', 'L'))
    )),

    decimal_floating_point_literal: $ => token(choice(
      seq(DIGITS, '.', optional(DIGITS), optional(seq((/[eE]/), optional(choice('-', '+')), DIGITS)), optional(/[fFdD]/)),
      seq('.', DIGITS, optional(seq((/[eE]/), optional(choice('-','+')), DIGITS)), optional(/[fFdD]/)),
      seq(DIGITS, /[eEpP]/, optional(choice('-','+')), DIGITS, optional(/[fFdD]/)),
      seq(DIGITS, optional(seq((/[eE]/), optional(choice('-','+')), DIGITS)), (/[fFdD]/))
    )),

    hex_floating_point_literal: $ => token(seq(
      choice('0x', '0X'),
      choice(
        seq(HEX_DIGITS, optional('.')),
        seq(optional(HEX_DIGITS), '.', HEX_DIGITS)
      ),
      optional(seq(
        /[eEpP]/,
        optional(choice('-','+')),
        DIGITS,
        optional(/[fFdD]/)
      ))
    )),

    true: $ => 'true',

    false: $ => 'false',

    character_literal: $ => token(seq(
      "'",
      repeat1(choice(
        /[^\\'\n]/,
        /\\./,
        /\\\n/
      )),
      "'"
    )),

    string_literal: $ => token(choice(
      seq('"', repeat(choice(/[^\\"\n]/, /\\(.|\n)/)), '"'),
      // TODO: support multiline string literals by debugging the following:
      // seq('"', repeat(choice(/[^\\"\n]/, /\\(.|\n)/)), '"', '+', /\n/, '"', repeat(choice(/[^\\"\n]/, /\\(.|\n)/)))
    )),

    null_literal: $ => 'null',

    // Expressions

    _expression: $ => choice(
      $.assignment_expression,
      $.binary_expression,
      $.instanceof_expression,
      $.lambda_expression,
      $.ternary_expression,
      $.update_expression,
      prec.dynamic(1, $._ambiguous_name),
      $._primary,
      $.unary_expression,
      $.cast_expression
    ),

    cast_expression: $ => prec(PREC.CAST, seq(
      '(',
      sep1(field('type', $._type), '&'),
      ')',
      field('value', $._expression)
    )),

    assignment_expression: $ => prec.right(PREC.ASSIGN, seq(
      field('left', choice(
        $._ambiguous_name,
        $.field_access,
        $.array_access
      )),
      field('operator', choice('=', '+=', '-=', '*=', '/=', '&=', '|=', '^=', '%=', '<<=', '>>=', '>>>=')),
      field('right', $._expression)
    )),

    binary_expression: $ => choice(
      ...[
      ['>', PREC.REL],
      ['<', PREC.REL],
      ['==', PREC.REL],
      ['>=', PREC.REL],
      ['<=', PREC.REL],
      ['!=', PREC.REL],
      ['&&', PREC.AND],
      ['||', PREC.OR],
      ['+', PREC.PLUS],
      ['-', PREC.PLUS],
      ['*', PREC.TIMES],
      ['/', PREC.TIMES],
      ['&', PREC.AND],
      ['|', PREC.OR],
      ['^', PREC.OR],
      ['%', PREC.TIMES],
      ['<<', PREC.TIMES],
      ['>>', PREC.TIMES],
      ['>>>', PREC.TIMES],
    ].map(([operator, precedence]) =>
      prec.left(precedence, seq(
        field('left', $._expression),
        field('operator', operator),
        field('right', $._expression)
      ))
    )),

    instanceof_expression: $ => prec(PREC.REL, seq(
      field('left', $._expression),
      'instanceof',
      field('right', $._type)
    )),

    lambda_expression: $ => seq(
      field('parameters', choice(
        $.identifier, $.formal_parameters, $.inferred_parameters
      )),
      '->',
      field('body', choice($._expression, $.block))
    ),

    inferred_parameters: $ => seq(
      '(',
      commaSep1($.identifier),
      ')'
    ),

    ternary_expression: $ => prec.right(PREC.TERNARY, seq(
      field('condition', $._expression),
      '?',
      field('consequence', $._expression),
      ':',
      field('alternative', $._expression)
    )),

    unary_expression: $ => choice(...[
      ['+', PREC.NEG],
      ['-', PREC.NEG],
      ['!', PREC.NOT],
      ['~', PREC.NOT],
    ].map(([operator, precedence]) =>
      prec.left(precedence, seq(
        field('operator', operator),
        field('operand', $._expression)
      ))
    )),

    update_expression: $ => prec.left(PREC.INC, choice(
      seq($._expression, '++'),
      seq($._expression, '--'),
      seq('++', $._expression),
      seq('--', $._expression)
    )),

    _primary: $ => choice(
      $._literal,
      $.class_literal,
      $.this,
      $.parenthesized_expression,
      $.object_creation_expression,
      $.field_access,
      $.array_access,
      $.method_invocation,
      $.method_reference,
      $.array_creation_expression
    ),

    array_creation_expression: $ => prec.right(seq(
      'new',
      field('type', $._simple_type),
      choice(
        seq(
          field('dimensions', repeat1($.dimensions_expr)),
          field('dimensions', optional($.dimensions))
        ),
        seq(
          field('dimensions', $.dimensions),
          field('value', $.array_initializer)
        )
      )
    )),

    dimensions_expr: $ => seq(repeat($._annotation), '[', $._expression, ']'),

    parenthesized_expression: $ => seq('(', $._expression, ')'),

    class_literal: $ => choice(
      seq($._ambiguous_name, repeat(seq('[', ']')), '.', 'class'),
      seq($._numeric_type, repeat(seq('[', ']')), '.', 'class'),
      seq($.boolean_type, repeat(seq('[', ']')), '.', 'class'),
      seq($.void_type, '.', 'class')
    ),

    object_creation_expression: $ => choice(
      $._unqualified_object_creation_expression,
      seq($._ambiguous_name, '.', $._unqualified_object_creation_expression),
      seq($._primary, '.', $._unqualified_object_creation_expression)
    ),

    _unqualified_object_creation_expression: $ => prec.right(seq(
      'new',
      field('type_arguments', optional($.type_arguments)),
      field('type', $._simple_type),
      field('arguments', $.argument_list),
      optional($.class_body)
    )),

    field_access: $ => choice(
      seq(
        field('object', $._ambiguous_name),
        '.',
        field('field', $.this)
      ),
      seq(
        field('object', choice($._primary, $.super)),
        '.',
        field('field', $.identifier)
      ),
      seq(
        field('object', $._ambiguous_name),
        '.',
        $.super,
        '.',
        field('field', $.identifier)
      )
    ),

    array_access: $ => seq(
      field('array', choice($._ambiguous_name, $._primary)),
      '[',
      field('index', $._expression),
      ']',
    ),

    method_invocation: $ => seq(
      choice(
        field('name', choice($.identifier, $._reserved_identifier)),
        seq(
          field('object', choice(
            $._ambiguous_name,
            $._primary,
            $.super,
            $._ambiguous_name
          )),
          '.',
          field('type_arguments', optional($.type_arguments)),
          field('name', $.identifier),
        ),
        seq(
          field('object', $._ambiguous_name),
          '.',
          $.super,
          '.',
          field('type_arguments', optional($.type_arguments)),
          field('name', $.identifier),
        )
      ),
      field('arguments', $.argument_list)
    ),

    argument_list: $ => seq('(', commaSep($._expression), ')'),

    method_reference: $ => seq(
      choice($._type, $._ambiguous_name, $._primary, $.super),
      '::',
      optional($.type_arguments),
      choice('new', $.identifier)
    ),

    type_arguments: $ => seq(
      '<',
      commaSep(choice($._type, $.wildcard)),
      '>'
    ),

    wildcard: $ => seq(
      repeat($._annotation),
      '?',
      optional($._wildcard_bounds)
    ),

    _wildcard_bounds: $ => choice(
      seq('extends', $._type),
      seq($.super, $._type)
    ),

    dimensions: $ => prec.right(repeat1(
      seq(repeat($._annotation), '[', ']')
    )),

    // Statements

    _statement: $ => choice(
      $._declaration,
      $.expression_statement,
      $.labeled_statement,
      $.if_statement,
      $.while_statement,
      $.for_statement,
      $.enhanced_for_statement,
      $.block,
      ';',
      $.assert_statement,
      $.switch_statement,
      $.do_statement,
      $.break_statement,
      $.continue_statement,
      $.return_statement,
      $.synchronized_statement,
      $.local_variable_declaration_statement,
      $.throw_statement,
      $.try_statement,
      $.try_with_resources_statement
    ),

    block: $ => seq(
      '{', repeat($._statement), '}'
    ),

    expression_statement: $ => seq(
      $._expression,
      ';'
    ),

    labeled_statement: $ => seq(
      $.identifier, ':', $._statement
    ),

    assert_statement: $ => choice(
      seq('assert', $._expression, ';'),
      seq('assert', $._expression, ':', $._expression, ';')
    ),

    switch_statement: $ => seq(
      'switch',
      field('condition', $.parenthesized_expression),
      field('body', $.switch_block)
    ),

    switch_block: $ => seq(
      '{',
      repeat(choice($.switch_label, $._statement)),
      '}'
    ),

    switch_label: $ => choice(
      seq('case', $._expression, ':'),
      seq('default', ':')
    ),

    do_statement: $ => seq(
      'do', $._statement, 'while', '(', $._expression, ')', ';'
    ),

    break_statement: $ => seq('break', optional($.identifier), ';'),

    continue_statement: $ => seq('continue', optional($.identifier), ';'),

    return_statement: $ => seq(
      'return',
      optional($._expression),
      ';'
    ),

    synchronized_statement: $ => seq('synchronized', '(', $._expression, ')', $.block),

    throw_statement: $ => seq('throw', $._expression, ';'),

    try_statement: $ => seq(
      'try',
      field('body', $.block),
      choice(
        repeat1($.catch_clause),
        seq(repeat($.catch_clause), $.finally_clause)
      )
    ),

    catch_clause: $ => seq(
      'catch',
      '(',
      $.catch_formal_parameter,
      ')',
      field('body', $.block)
    ),

    catch_formal_parameter: $ => seq(
      optional($.modifiers),
      $.catch_type,
      $._variable_declarator_id
    ),

    catch_type: $ => sep1($._unannotated_type, '|'),

    finally_clause: $ => seq('finally', $.block),

    try_with_resources_statement: $ => seq(
      'try',
      field('resources', $.resource_specification),
      field('body', $.block),
      repeat($.catch_clause),
      optional($.finally_clause)
    ),

    resource_specification: $ => seq(
      '(', sep1($.resource, ';'), optional(';'), ')'
    ),

    resource: $ => choice(
      seq(
        optional($.modifiers),
        field('type', $._unannotated_type),
        $._variable_declarator_id,
        '=',
        field('value', $._expression)
      ),
      $._ambiguous_name,
      $.field_access
    ),

    if_statement: $ => prec.right(seq(
      'if',
      field('condition', $.parenthesized_expression),
      field('consequence', $._statement),
      optional(seq('else', field('alternative', $._statement)))
    )),

    while_statement: $ => seq(
      'while',
      field('condition', $.parenthesized_expression),
      field('body', $._statement)
    ),

    for_statement: $ => seq(
      'for', '(',
      optional($.for_init), ';',
      optional($._expression), ';',
      commaSep($._expression), ')',
      $._statement
    ),

    for_init: $ => choice(
      commaSep1($._expression),
      $.local_variable_declaration,
    ),

    enhanced_for_statement: $ => seq(
      'for',
      '(',
      optional($.modifiers),
      field('type', $._unannotated_type),
      $._variable_declarator_id,
      ':',
      field('value', $._expression),
      ')',
      field('body', $._statement)
    ),

    // Annotations

    _annotation: $ => choice(
      $.marker_annotation,
      $.annotation
    ),

    marker_annotation: $ => seq(
      '@',
      field('name', choice($.identifier, $.scoped_identifier))
    ),

    annotation: $ => seq(
      '@',
      field('name', choice($.identifier, $.scoped_identifier)),
      field('arguments', $.annotation_argument_list)
    ),

    annotation_argument_list: $ => seq(
      '(',
      choice(
        $._element_value,
        commaSep($.element_value_pair),
      ),
      ')'
    ),

    element_value_pair: $ => seq(
      field('key', $.identifier),
      '=',
      field('value', $._element_value)
    ),

    _element_value: $ => prec(1, choice(
      $._expression,
      $.element_value_array_initializer,
      $._annotation
    )),

    element_value_array_initializer: $ => seq(
      '{',
      commaSep($._element_value),
      optional(','),
      '}'
    ),

    // Declarations

    _declaration: $ => prec(1, choice(
      $.module_declaration,
      $.package_declaration,
      $.import_declaration,
      $.class_declaration,
      $.interface_declaration,
      $.annotation_type_declaration,
      $.enum_declaration,
    )),

    module_declaration: $ => seq(
      repeat($._annotation),
      optional('open'),
      'module',
      $._ambiguous_name,
      '{',
      repeat($.module_directive),
      '}'
    ),

    module_directive: $ => seq(choice(
      seq('requires', repeat($.requires_modifier), $.module_name),
      seq('exports', $._ambiguous_name, optional('to'), optional($.module_name), repeat(seq(',', $.module_name))),
      seq('opens', $._ambiguous_name, optional('to'), optional($.module_name), repeat(seq(',', $.module_name))),
      seq('uses', $._ambiguous_name),
      seq('provides', $._ambiguous_name, 'with', $._ambiguous_name, repeat(seq(',', $._ambiguous_name)))
    ), ';'),

    requires_modifier: $ => choice(
      'transitive',
      'static'
    ),

    module_name: $ => choice(
      $.identifier,
      seq($.module_name, '.', $.identifier)
    ),

    package_declaration: $ => seq(
      repeat($._annotation),
      'package',
      $._ambiguous_name,
      ';'
    ),

    import_declaration: $ => seq(
      'import',
      optional('static'),
      sep1($.identifier, '.'),
      optional(seq('.', $.asterisk)),
      ';'
    ),

    asterisk: $ => '*',

    enum_declaration: $ => seq(
      optional($.modifiers),
      'enum',
      field('name', $.identifier),
      field('interfaces', optional($.super_interfaces)),
      field('body', $.enum_body)
    ),

    enum_body: $ => seq(
      '{',
      commaSep($.enum_constant),
      optional(','),
      optional($.enum_body_declarations),
      '}'
    ),

    enum_body_declarations: $ => seq(
      ';',
      repeat($._class_body_declaration)
    ),

    enum_constant: $ => (seq(
      optional($.modifiers),
      field('name', $.identifier),
      field('arguments', optional($.argument_list)),
      field('body', optional($.class_body))
    )),

    class_declaration: $ => seq(
      optional($.modifiers),
      'class',
      field('name', $.identifier),
      optional(field('type_parameters', $.type_parameters)),
      optional(field('superclass', $.superclass)),
      optional(field('interfaces', $.super_interfaces)),
      field('body', $.class_body)
    ),

    modifiers: $ => repeat1(choice(
      $._annotation,
      'public',
      'protected',
      'private',
      'abstract',
      'static',
      'final',
      'strictfp',
      'default',
      'synchronized',
      'native',
      'transient',
      'volatile'
    )),

    type_parameters: $ => seq(
      '<', commaSep1($.type_parameter), '>'
    ),

    type_parameter: $ => seq(
      repeat($._annotation),
      $.identifier,
      optional($.type_bound)
    ),

    type_bound: $ => seq('extends', $._type, repeat(seq('&', $._type))),

    superclass: $ => seq(
      'extends',
      $._type
    ),

    super_interfaces: $ => seq(
      'implements',
      $.interface_type_list
    ),

    interface_type_list: $ => seq(
      $._type,
      repeat(seq(',', $._type))
    ),

    class_body: $ => seq(
      '{',
      repeat($._class_body_declaration),
      '}'
    ),

    _class_body_declaration: $ => choice(
      $._class_member_declaration,
      $.block,
      $.static_initializer,
      $.constructor_declaration
    ),

    static_initializer: $ => seq(
      'static',
      $.block
    ),

    constructor_declaration: $ => seq(
      optional($.modifiers),
      $._constructor_declarator,
      optional($.throws),
      field('body', $.constructor_body)
    ),

    _constructor_declarator: $ => seq(
      field('type_paramaters', optional($.type_parameters)),
      field('name', $.identifier),
      field('parameters', $.formal_parameters)
    ),

    constructor_body: $ => seq(
      '{',
      optional($.explicit_constructor_invocation),
      repeat($._statement),
      '}'
    ),

    explicit_constructor_invocation: $ => seq(
      choice(
        seq(
          field('type_arguments', optional($.type_arguments)),
          field('constructor', choice($.this, $.super)),
        ),
        seq(
          field('object', choice($._ambiguous_name, $._primary)),
          '.',
          field('type_arguments', optional($.type_arguments)),
          field('constructor', $.super),
        )
      ),
      field('arguments', $.argument_list),
      ';'
    ),

    _ambiguous_name: $ => choice(
      $.identifier,
      $._reserved_identifier,
      $.scoped_identifier
    ),

    scoped_identifier: $ => seq(
      choice($.identifier, $._reserved_identifier, $.scoped_identifier),
      '.',
      $.identifier
    ),

    _class_member_declaration: $ => choice(
      $.field_declaration,
      $.method_declaration,
      $.class_declaration,
      $.interface_declaration,
      $.annotation_type_declaration,
      $.enum_declaration,
      ';'
    ),

    field_declaration: $ => seq(
      optional($.modifiers),
      field('type', $._unannotated_type),
      $._variable_declarator_list,
      ';'
    ),

    annotation_type_declaration: $ => seq(
      optional($.modifiers),
      '@interface',
      field('name', $.identifier),
      field('body', $.annotation_type_body)
    ),

    annotation_type_body: $ => seq(
      '{', repeat($._annotation_type_member_declaration), '}'
    ),

    _annotation_type_member_declaration: $ => choice(
      $.annotation_type_element_declaration,
      $.constant_declaration,
      $.class_declaration,
      $.interface_declaration,
      $.annotation_type_declaration
    ),

    annotation_type_element_declaration: $ => seq(
      optional($.modifiers),
      field('type', $._unannotated_type),
      field('name', $.identifier),
      '(', ')',
      field('dimensions', optional($.dimensions)),
      optional($._default_value),
      ';'
    ),

    _default_value: $ => seq(
      'default',
      field('value', $._element_value)
    ),

    interface_declaration: $ => seq(
      optional($.modifiers),
      'interface',
      field('name', $.identifier),
      field('type_parameters', optional($.type_parameters)),
      optional($.extends_interfaces),
      field('body', $.interface_body)
    ),

    extends_interfaces: $ => seq(
      'extends',
      $.interface_type_list
    ),

    interface_body: $ => seq(
      '{',
      repeat($._interface_member_declaration),
      '}'
    ),

    _interface_member_declaration: $ => choice(
      $.constant_declaration,
      $.enum_declaration,
      $.method_declaration,
      $.class_declaration,
      $.interface_declaration,
      $.annotation_type_declaration,
      ';'
    ),

    constant_declaration: $ => seq(
      optional($.modifiers),
      field('type', $._unannotated_type),
      $._variable_declarator_list,
      ';'
    ),

    _variable_declarator_list: $ => commaSep1(
      field('declarator', $.variable_declarator)
    ),

    variable_declarator: $ => seq(
      $._variable_declarator_id,
      optional(seq('=', field('value', $._variable_initializer)))
    ),

    _variable_declarator_id: $ => seq(
      field('name', choice($.identifier, $._reserved_identifier)),
      field('dimensions', optional($.dimensions))
    ),

    _variable_initializer: $ => choice(
      $._expression,
      $.array_initializer
    ),

    array_initializer: $ => seq(
      '{',
      commaSep($._variable_initializer),
      optional(','),
      '}'
    ),

    // Types

    _type: $ => choice(
      $._unannotated_type,
      $.annotated_type
    ),

    _unannotated_type: $ => choice(
      $._simple_type,
      $.array_type
    ),

    _simple_type: $ => choice(
      $.void_type,
      $._numeric_type,
      $.boolean_type,
      alias($.identifier, $.type_identifier),
      $.scoped_type_identifier,
      $.generic_type
    ),

    annotated_type: $ => seq(
      repeat1($._annotation),
      $._unannotated_type
    ),

    scoped_type_identifier: $ => seq(
      choice(
        alias($.identifier, $.type_identifier),
        $.scoped_type_identifier,
        $.generic_type
      ),
      '.',
      repeat($._annotation),
      alias($.identifier, $.type_identifier)
    ),

    generic_type: $ => prec.dynamic(10, seq(
      choice(
        alias($.identifier, $.type_identifier),
        $.scoped_type_identifier
      ),
      $.type_arguments
    )),

    array_type: $ => seq(
      field('element', $._unannotated_type),
      field('dimensions', $.dimensions)
    ),

    _numeric_type: $ => choice(
      $.integral_type,
      $.floating_point_type
    ),

    integral_type: $ => choice(
      'byte',
      'short',
      'int',
      'long',
      'char'
    ),

    floating_point_type: $ => choice(
      'float',
      'double'
    ),

    boolean_type: $ => 'boolean',

    void_type: $ => 'void',

    _method_header: $ => seq(
      optional(seq(
        field('type_parameters', $.type_parameters),
        repeat($._annotation)
      )),
      field('type', $._unannotated_type),
      $._method_declarator,
      optional($.throws)
    ),

    _method_declarator: $ => seq(
      field('name', choice($.identifier, $._reserved_identifier)),
      field('parameters', $.formal_parameters),
      field('dimensions', optional($.dimensions))
    ),

    formal_parameters: $ => seq(
      '(',
      optional($.receiver_parameter),
      commaSep($.formal_parameter),
      optional(','),
      optional($.spread_parameter),
      ')'
    ),

    formal_parameter: $ => seq(
      optional($.modifiers),
      field('type', $._unannotated_type),
      $._variable_declarator_id
    ),

    receiver_parameter: $ => seq(
      repeat($._annotation),
      $._unannotated_type,
      optional(seq($.identifier, '.')),
      $.this
    ),

    spread_parameter: $ => seq(
      optional($.modifiers),
      $._unannotated_type,
      '...',
      $.variable_declarator
    ),

    throws: $ => seq(
      'throws', commaSep1($._type)
    ),

    local_variable_declaration_statement: $ => seq(
      $.local_variable_declaration,
      ';'
    ),

    local_variable_declaration: $ => seq(
      optional($.modifiers),
      field('type', $._unannotated_type),
      $._variable_declarator_list
    ),

    method_declaration: $ => seq(
      optional($.modifiers),
      $._method_header,
      choice(field('body', $.block), ';')
    ),

    _reserved_identifier: $ => alias(choice(
      'open',
      'module'
    ), $.identifier),

    this: $ => 'this',

    super: $ => 'super',

    identifier: $ => /[a-zA-Z_]\w*/,

    // http://stackoverflow.com/questions/13014947/regex-to-match-a-c-style-multiline-comment/36328890#36328890
    comment: $ => token(prec(PREC.COMMENT, choice(
      seq('//', /.*/),
      seq(
        '/*',
        /[^*]*\*+([^/*][^*]*\*+)*/,
        '/'
      )
    ))),
  }
});

function sep1 (rule, separator) {
  return seq(rule, repeat(seq(separator, rule)));
}

function commaSep1(rule) {
  return seq(rule, repeat(seq(',', rule)))
}

function commaSep(rule) {
  return optional(commaSep1(rule))
}
