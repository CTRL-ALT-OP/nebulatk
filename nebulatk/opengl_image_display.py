import ctypes

try:
    import glfw
    from OpenGL import GL
except Exception:
    glfw = None
    GL = None


VERTEX_SRC_330 = """
#version 330 core
layout (location = 0) in vec2 a_pos;
layout (location = 1) in vec2 a_uv;
out vec2 v_uv;
void main() {
    v_uv = a_uv;
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
"""

FRAGMENT_SRC_330 = """
#version 330 core
in vec2 v_uv;
out vec4 FragColor;
uniform sampler2D u_texture;
void main() {
    FragColor = texture(u_texture, v_uv);
}
"""

VERTEX_SRC_120 = """
#version 120
attribute vec2 a_pos;
attribute vec2 a_uv;
varying vec2 v_uv;
void main() {
    v_uv = a_uv;
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
"""

FRAGMENT_SRC_120 = """
#version 120
varying vec2 v_uv;
uniform sampler2D u_texture;
void main() {
    gl_FragColor = texture2D(u_texture, v_uv);
}
"""


class OpenGLImageDisplay:
    def __init__(self, root, width, height):
        self._proxy_mode = hasattr(root, "submit_frame")
        self._enabled = glfw is not None and GL is not None
        self._texture_id = None
        self._program_id = None
        self._vbo_id = None
        self._vao_id = None
        self._pos_loc = -1
        self._uv_loc = -1
        self._sampler_loc = -1
        self._frame_rgba = None
        self._needs_texture_upload = False
        self._texture_size = (0, 0)
        self.width = int(width)
        self.height = int(height)
        self.root = root
        self.canvas = root

        if self._proxy_mode:
            return
        if not self._enabled:
            raise RuntimeError(
                "OpenGL backend unavailable. Install/enable glfw + PyOpenGL."
            )
        self._init_gl()

    def _init_gl(self):
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        self._texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        self._program_id = self._build_program()
        self._setup_fullscreen_quad()

    def _compile_shader(self, shader_type, source):
        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)
        if GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS) != GL.GL_TRUE:
            log = GL.glGetShaderInfoLog(shader)
            GL.glDeleteShader(shader)
            raise RuntimeError(f"OpenGL shader compile failed: {log}")
        return shader

    def _build_program(self):
        variants = [
            (VERTEX_SRC_330, FRAGMENT_SRC_330, True),
            (VERTEX_SRC_120, FRAGMENT_SRC_120, False),
        ]
        last_error = None

        for vertex_src, fragment_src, explicit_locations in variants:
            program = None
            vertex = None
            fragment = None
            try:
                vertex = self._compile_shader(GL.GL_VERTEX_SHADER, vertex_src)
                fragment = self._compile_shader(GL.GL_FRAGMENT_SHADER, fragment_src)
                program = GL.glCreateProgram()
                GL.glAttachShader(program, vertex)
                GL.glAttachShader(program, fragment)
                if not explicit_locations:
                    GL.glBindAttribLocation(program, 0, "a_pos")
                    GL.glBindAttribLocation(program, 1, "a_uv")
                GL.glLinkProgram(program)
                if GL.glGetProgramiv(program, GL.GL_LINK_STATUS) != GL.GL_TRUE:
                    log = GL.glGetProgramInfoLog(program)
                    raise RuntimeError(f"OpenGL program link failed: {log}")
                GL.glDeleteShader(vertex)
                GL.glDeleteShader(fragment)
                self._pos_loc = GL.glGetAttribLocation(program, "a_pos")
                self._uv_loc = GL.glGetAttribLocation(program, "a_uv")
                self._sampler_loc = GL.glGetUniformLocation(program, "u_texture")
                return program
            except Exception as exc:
                last_error = exc
                if program is not None:
                    GL.glDeleteProgram(program)
                if vertex is not None:
                    GL.glDeleteShader(vertex)
                if fragment is not None:
                    GL.glDeleteShader(fragment)
                continue

        raise RuntimeError(f"Failed to initialize OpenGL shader pipeline: {last_error}")

    def _setup_fullscreen_quad(self):
        vertex_data = (
            -1.0,
            -1.0,
            0.0,
            1.0,
            1.0,
            -1.0,
            1.0,
            1.0,
            -1.0,
            1.0,
            0.0,
            0.0,
            1.0,
            1.0,
            1.0,
            0.0,
        )
        vertices = (ctypes.c_float * len(vertex_data))(*vertex_data)
        self._vbo_id = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo_id)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            ctypes.sizeof(vertices),
            vertices,
            GL.GL_STATIC_DRAW,
        )

        # Core profiles require a VAO; compatibility profiles can draw without one.
        if hasattr(GL, "glGenVertexArrays"):
            try:
                self._vao_id = GL.glGenVertexArrays(1)
                GL.glBindVertexArray(self._vao_id)
            except Exception:
                self._vao_id = None

        stride = 4 * 4
        if self._pos_loc >= 0:
            GL.glEnableVertexAttribArray(self._pos_loc)
            GL.glVertexAttribPointer(
                self._pos_loc, 2, GL.GL_FLOAT, False, stride, ctypes.c_void_p(0)
            )
        if self._uv_loc >= 0:
            GL.glEnableVertexAttribArray(self._uv_loc)
            GL.glVertexAttribPointer(
                self._uv_loc, 2, GL.GL_FLOAT, False, stride, ctypes.c_void_p(8)
            )

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        if self._vao_id is not None:
            GL.glBindVertexArray(0)

    def _bind_quad(self):
        if self._vao_id is not None:
            GL.glBindVertexArray(self._vao_id)
            return
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo_id)
        stride = 4 * 4
        if self._pos_loc >= 0:
            GL.glEnableVertexAttribArray(self._pos_loc)
            GL.glVertexAttribPointer(
                self._pos_loc, 2, GL.GL_FLOAT, False, stride, ctypes.c_void_p(0)
            )
        if self._uv_loc >= 0:
            GL.glEnableVertexAttribArray(self._uv_loc)
            GL.glVertexAttribPointer(
                self._uv_loc, 2, GL.GL_FLOAT, False, stride, ctypes.c_void_p(8)
            )

    def _unbind_quad(self):
        if self._vao_id is not None:
            GL.glBindVertexArray(0)
            return
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        if self._pos_loc >= 0:
            GL.glDisableVertexAttribArray(self._pos_loc)
        if self._uv_loc >= 0:
            GL.glDisableVertexAttribArray(self._uv_loc)

    def show_frame(self, frame):
        rgba = frame.convert("RGBA")
        self.width, self.height = rgba.size
        frame_rgba = rgba.tobytes("raw", "RGBA")
        if self._proxy_mode:
            self.root.submit_frame(frame_rgba, self.width, self.height)
            return
        self._frame_rgba = frame_rgba
        self._needs_texture_upload = True

    def show_frame_bytes(self, frame_rgba, width, height):
        self.width = int(width)
        self.height = int(height)
        self._frame_rgba = frame_rgba
        self._needs_texture_upload = True

    def draw(self):
        if self._proxy_mode:
            return
        framebuffer_width, framebuffer_height = glfw.get_framebuffer_size(
            self.root.handle
        )
        if framebuffer_width <= 0 or framebuffer_height <= 0:
            return
        # Keep content at a fixed pixel size and anchor to top-left.
        # Window resizing should change only the visible/canvas area, not scale content.
        viewport_x = 0
        viewport_y = framebuffer_height - self.height
        GL.glViewport(viewport_x, viewport_y, self.width, self.height)
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        if self._frame_rgba is None or self._texture_id is None:
            return

        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        if self._needs_texture_upload:
            if self._texture_size != (self.width, self.height):
                GL.glTexImage2D(
                    GL.GL_TEXTURE_2D,
                    0,
                    GL.GL_RGBA,
                    self.width,
                    self.height,
                    0,
                    GL.GL_RGBA,
                    GL.GL_UNSIGNED_BYTE,
                    self._frame_rgba,
                )
                self._texture_size = (self.width, self.height)
            else:
                GL.glTexSubImage2D(
                    GL.GL_TEXTURE_2D,
                    0,
                    0,
                    0,
                    self.width,
                    self.height,
                    GL.GL_RGBA,
                    GL.GL_UNSIGNED_BYTE,
                    self._frame_rgba,
                )
            self._needs_texture_upload = False

        GL.glUseProgram(self._program_id)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)
        if self._sampler_loc >= 0:
            GL.glUniform1i(self._sampler_loc, 0)

        self._bind_quad()
        GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)
        self._unbind_quad()
        GL.glUseProgram(0)

    def configure(self, width=None, height=None):
        if width is not None:
            self.width = int(width)
        if height is not None:
            self.height = int(height)
