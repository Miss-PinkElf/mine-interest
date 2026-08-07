package com.mineinterest.media.core.path

import com.mineinterest.media.core.CoreConstants
import com.mineinterest.media.core.model.Platform
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class SavePathPolicyTest {

    @Test
    fun sanitize_removes_illegal_chars() {
        val name = SavePathPolicy.sanitizeFileName("a/b:c*|?.txt")
        assertFalse(name.contains("/"))
        assertFalse(name.contains(":"))
        assertFalse(name.contains("*"))
        assertTrue(name.contains(".txt") || name.contains("_"))
    }

    @Test
    fun defaultRelativeDir_matches_constants() {
        assertEquals(
            CoreConstants.DEFAULT_BILI_SUBDIR,
            SavePathPolicy.defaultRelativeDir(Platform.BILIBILI),
        )
        assertEquals(
            CoreConstants.DEFAULT_FANQIE_SUBDIR,
            SavePathPolicy.defaultRelativeDir(Platform.FANQIE),
        )
    }
}
