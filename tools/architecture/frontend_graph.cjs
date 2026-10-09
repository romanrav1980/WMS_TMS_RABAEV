// Read-only TypeScript AST inventory, using the frontend's installed compiler.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(process.argv[2]);
const project = path.resolve(root, process.argv[3]);
const compilerProject = process.argv[4] ? path.resolve(process.argv[4]) : project;
const ts = require(path.join(compilerProject, 'node_modules/typescript/lib/typescript.js'));
const configPath = ts.findConfigFile(project, ts.sys.fileExists, 'tsconfig.json');
const config = ts.readConfigFile(configPath, ts.sys.readFile);
if (config.error) throw new Error(ts.flattenDiagnosticMessageText(config.error.messageText, '\n'));
const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, project);
if (parsed.errors.length) throw new Error(parsed.errors.map(e => ts.flattenDiagnosticMessageText(e.messageText, '\n')).join('\n'));
const relative = file => path.relative(root, file).split(path.sep).join('/');
const records = [];
for (const file of parsed.fileNames.map(f => path.resolve(f)).filter(f => /\.(ts|tsx)$/.test(f) && f.startsWith(path.join(project, 'src') + path.sep))) {
  const text = fs.readFileSync(file, 'utf8');
  const source = ts.createSourceFile(file, text, ts.ScriptTarget.Latest, true);
  const record = {path: relative(file), lines: text.split(/\r?\n/).length, imports: [], functions: [], errors: []};
  for (const error of source.parseDiagnostics) record.errors.push(ts.flattenDiagnosticMessageText(error.messageText, '\n'));
  function visit(node) {
    let specifier;
    let typeOnly = false;
    if (ts.isImportDeclaration(node) || ts.isExportDeclaration(node)) {
      specifier = node.moduleSpecifier;
      typeOnly = Boolean(node.isTypeOnly || (node.importClause && (node.importClause.isTypeOnly ||
        (!node.importClause.name && node.importClause.namedBindings && ts.isNamedImports(node.importClause.namedBindings) &&
         node.importClause.namedBindings.elements.length && node.importClause.namedBindings.elements.every(e => e.isTypeOnly)))));
    } else if (ts.isCallExpression(node) && (node.expression.kind === ts.SyntaxKind.ImportKeyword ||
               (ts.isIdentifier(node.expression) && node.expression.text === 'require'))) {
      specifier = node.arguments[0];
      if (!specifier || !ts.isStringLiteral(specifier)) record.errors.push('Non-literal dynamic import requires explicit architecture review');
    }
    if (specifier && ts.isStringLiteral(specifier)) {
      const resolved = ts.resolveModuleName(specifier.text, file, parsed.options, ts.sys).resolvedModule;
      if (resolved && !resolved.isExternalLibraryImport && path.resolve(resolved.resolvedFileName).startsWith(root + path.sep)) {
        record.imports.push({target: relative(path.resolve(resolved.resolvedFileName)), typeOnly});
      } else if (!resolved && specifier.text.startsWith('.') && !fs.existsSync(path.resolve(path.dirname(file), specifier.text))) record.errors.push('Unresolved local import: ' + specifier.text);
    }
    if (ts.isFunctionDeclaration(node) || ts.isMethodDeclaration(node) || ts.isArrowFunction(node) || ts.isFunctionExpression(node)) {
      const names = [];
      for (let parent = node; parent && !ts.isSourceFile(parent); parent = parent.parent) {
        if (parent.name && (ts.isIdentifier(parent.name) || ts.isStringLiteral(parent.name))) names.unshift(parent.name.text);
      }
      record.functions.push({name: names.join('.') || '<anonymous>', lines:
        source.getLineAndCharacterOfPosition(node.end).line - source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1});
    }
    ts.forEachChild(node, visit);
  }
  visit(source);
  records.push(record);
}
if (!records.length) throw new Error('No frontend source files inspected');
process.stdout.write(JSON.stringify(records));
