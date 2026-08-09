#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

static int append_module_path(PyConfig *config, const char *root,
                              const char *suffix) {
  char path[PATH_MAX];
  if (snprintf(path, sizeof(path), "%s%s", root, suffix) >= sizeof(path)) {
    fprintf(stderr, "PicoC Compiler installation path is too long\n");
    return -1;
  }

  wchar_t *wide_path = Py_DecodeLocale(path, NULL);
  if (wide_path == NULL) {
    return -1;
  }
  PyStatus status = PyWideStringList_Append(&config->module_search_paths,
                                            wide_path);
  PyMem_RawFree(wide_path);
  return PyStatus_Exception(status) ? -1 : 0;
}

int main(int argc, char **argv) {
  const char *root = getenv("PICOC_COMPILER_ROOT");
  if (root == NULL || root[0] == '\0') {
    fprintf(stderr, "PICOC_COMPILER_ROOT is not set; use the picoc_compiler launcher\n");
    return 1;
  }

  char python_home[PATH_MAX];
  if (snprintf(python_home, sizeof(python_home), "%s/runtime", root) >=
      sizeof(python_home)) {
    fprintf(stderr, "PicoC Compiler installation path is too long\n");
    return 1;
  }

  PyConfig config;
  PyConfig_InitPythonConfig(&config);
  config.isolated = 1;
  config.parse_argv = 0;
  config.site_import = 0;
  config.use_environment = 0;
  config.module_search_paths_set = 1;

  wchar_t *wide_home = Py_DecodeLocale(python_home, NULL);
  if (wide_home == NULL) {
    PyConfig_Clear(&config);
    return 1;
  }
  PyStatus status = PyConfig_SetString(&config, &config.home, wide_home);
  PyMem_RawFree(wide_home);
  if (PyStatus_Exception(status) ||
      PyStatus_Exception(PyConfig_SetBytesArgv(&config, argc, argv)) ||
      append_module_path(&config, root, "/app") != 0 ||
      append_module_path(&config, root, "/lib/python") != 0 ||
      append_module_path(&config, root, "/runtime/lib/python3.14") != 0 ||
      append_module_path(&config, root,
                         "/runtime/lib/python3.14/lib-dynload") != 0) {
    PyConfig_Clear(&config);
    fprintf(stderr, "Failed to configure the bundled Python runtime\n");
    return 1;
  }

  status = Py_InitializeFromConfig(&config);
  PyConfig_Clear(&config);
  if (PyStatus_Exception(status)) {
    Py_ExitStatusException(status);
  }

  int result = PyRun_SimpleString("from source.main import main\nmain()\n");
  if (result != 0) {
    PyErr_Print();
  }
  if (Py_FinalizeEx() < 0) {
    return 120;
  }
  return result == 0 ? 0 : 1;
}
